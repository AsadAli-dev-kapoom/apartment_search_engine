# This file tests the monitoring layer with real SQLite storage.
# It verifies that a newly discovered listing is persisted and
# is not reported again on the next monitoring check.

from app.models import Listing
from app.monitoring import ApartmentListingMonitor
from app.sources.base import ApartmentSource
from app.storage.sqlite import SQLiteListingRepository


class FakeSource(ApartmentSource):
    """Test source that returns predefined listings."""

    name = "fake"

    def __init__(self, listings: list[Listing]):
        self.listings = listings

    def fetch_listings(self) -> list[Listing]:
        return self.listings


def test_monitor_detects_listing_only_once(tmp_path):

    listing = Listing(
        source="fake",
        listing_id="123",
        url="https://example.com/123",
    )

    source = FakeSource([listing])

    repository = SQLiteListingRepository(
        str(tmp_path / "listings.db")
    )

    monitor = ApartmentListingMonitor(
        source=source,
        repository=repository,
    )

    first_check = monitor.check()
    second_check = monitor.check()

    assert first_check == [listing]
    assert second_check == []

    stored = repository.get("fake", "123")

    assert stored is not None
    assert stored.listing_id == "123"
    assert stored.first_seen_at is not None
    assert stored.last_seen_at is not None