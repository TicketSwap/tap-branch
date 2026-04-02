"""Branch export stream base class."""

from __future__ import annotations

import contextlib
import csv
import gzip
import io
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar

import requests
from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from singer_sdk.helpers.types import Context

EXPORT_URL = "https://api2.branch.io/v3/export"


class BranchExportStream(Stream):
    """Base class for Branch daily export streams.

    Calls the Branch /v3/export API for each date in the sync range,
    downloads the resulting CSV files from S3, and emits records.
    """

    replication_key = "export_date"
    event_type: ClassVar[str]  # set by each subclass, e.g. "eo_click"

    def get_records(self, context: Context | None) -> Iterable[dict[str, Any]]:
        """Yield records by iterating over each day in the sync range."""
        start = self.get_starting_timestamp(context).replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.now().astimezone(start.tzinfo).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        while start <= end:
            self.logger.info("Syncing %s for %s", self.name, start)
            urls = self._get_export_urls(start)
            total = len(urls)
            for i, url in enumerate(urls, start=1):
                self.logger.info(
                    "Downloading CSV file %d/%d for %s on %s", i, total, self.name, start.date()
                )
                yield from self._parse_csv(url, start)
            start += timedelta(days=1)

    def _fetch_export_urls_for_date(self, export_date: date) -> dict[str, list[str]]:
        """Fetch all event-type URLs for a given date, with tap-level caching."""
        cache: dict[date, dict[str, list[str]]] = self._tap.__dict__.setdefault(
            "_export_url_cache", {}
        )
        if export_date not in cache:
            response = requests.post(
                EXPORT_URL,
                json={
                    "branch_key": self.config["api_key"],
                    "branch_secret": self.config["api_secret"],
                    "export_date": export_date.strftime("%Y-%m-%d"),
                },
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=60,
            )
            response.raise_for_status()
            cache[export_date] = response.json()
        return cache[export_date]

    def _get_export_urls(self, export_date: datetime) -> list[str]:
        return self._fetch_export_urls_for_date(export_date.date()).get(self.event_type, [])

    def post_process(self, row: dict, context: Context | None = None) -> dict | None:  # noqa: ARG002
        for key, prop in self.schema.get("properties", {}).items():
            if key not in row:
                continue
            types = prop.get("type", [])
            if isinstance(types, str):
                types = [types]
            if row[key] in (None, ""):
                row[key] = None if "null" in types else row[key]
                continue
            if "integer" in types and isinstance(row[key], str):
                with contextlib.suppress(ValueError, TypeError):
                    row[key] = int(row[key])
            elif "number" in types and isinstance(row[key], str):
                with contextlib.suppress(ValueError, TypeError):
                    row[key] = float(row[key])
        return row

    def _parse_csv(self, url: str, export_date: datetime) -> Iterable[dict[str, Any]]:
        resp = requests.get(url, timeout=300)
        resp.raise_for_status()
        content = resp.content
        if content[:2] == b"\x1f\x8b":
            content = gzip.decompress(content)
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        for row in reader:
            row["export_date"] = export_date
            yield row
