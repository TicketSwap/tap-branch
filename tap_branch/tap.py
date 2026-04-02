"""Branch tap class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_branch import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from tap_branch.client import BranchExportStream


class TapBranch(Tap):
    """Singer tap for Branch."""

    name = "tap-branch"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "branch_key",
            th.StringType(nullable=False),
            required=True,
            secret=True,
            title="Branch Key",
            description="The Branch app key (public).",
        ),
        th.Property(
            "branch_secret",
            th.StringType(nullable=False),
            required=True,
            secret=True,
            title="Branch Secret",
            description="The Branch app secret.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=False),
            required=True,
            description=(
                "The earliest export date to sync, in YYYY-MM-DDTHH:MM:SSZ format. "
            ),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[BranchExportStream]:
        """Return a list of discovered streams."""
        return [
            streams.EoClickStream(self),
            streams.EoImpressionStream(self),
            streams.EoInstallStream(self),
            streams.EoOpenStream(self),
            streams.EoReinstallStream(self),
            streams.EoCommerceEventStream(self),
            streams.EoCustomEventStream(self),
            streams.EoWebSessionStartStream(self),
        ]


if __name__ == "__main__":
    TapBranch.cli()
