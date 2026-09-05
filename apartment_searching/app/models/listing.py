# This file defines the common Listing model used by all apartment sources.
# It contains only the information needed to identify a listing and track it over time.

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Listing:
    """A normalized apartment listing."""

    source: str
    listing_id: str
    url: str

    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None