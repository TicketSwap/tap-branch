"""Stream type classes for tap-branch."""

from __future__ import annotations

from tap_branch import schemas
from tap_branch.client import BranchExportStream


class EoClickStream(BranchExportStream):
    """CLICK — user-initiated tap on a Branch link."""

    name = "eo_click"
    event_type = "eo_click"
    primary_keys = ("id",)
    schema = schemas.EO_CLICK


class EoImpressionStream(BranchExportStream):
    """IMPRESSION — loading of a user-placed impression pixel."""

    name = "eo_impression"
    event_type = "eo_impression"
    primary_keys = ("id",)
    schema = schemas.EO_IMPRESSION


class EoInstallStream(BranchExportStream):
    """INSTALL — first app launch for a given device."""

    name = "eo_install"
    event_type = "eo_install"
    primary_keys = ("id",)
    schema = schemas.EO_INSTALL


class EoOpenStream(BranchExportStream):
    """OPEN — mobile app launch that is not an install."""

    name = "eo_open"
    event_type = "eo_open"
    primary_keys = ("id",)
    schema = schemas.EO_OPEN


class EoReinstallStream(BranchExportStream):
    """REINSTALL — app deleted then re-installed on the same device."""

    name = "eo_reinstall"
    event_type = "eo_reinstall"
    primary_keys = ("id",)
    schema = schemas.EO_REINSTALL


class EoCommerceEventStream(BranchExportStream):
    """COMMERCE_EVENT — add to cart, purchase, and other commerce actions."""

    name = "eo_commerce_event"
    event_type = "eo_commerce_event"
    primary_keys = ("id",)
    schema = schemas.EO_COMMERCE_EVENT


class EoCustomEventStream(BranchExportStream):
    """CUSTOM_EVENT — non-standard Branch event."""

    name = "eo_custom_event"
    event_type = "eo_custom_event"
    primary_keys = ("id",)
    schema = schemas.EO_CUSTOM_EVENT


class EoWebSessionStartStream(BranchExportStream):
    """WEB_SESSION_START — first page view of a website session."""

    name = "eo_web_session_start"
    event_type = "eo_web_session_start"
    primary_keys = ("id",)
    schema = schemas.EO_WEB_SESSION_START
