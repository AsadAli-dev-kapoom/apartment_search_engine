# This file tests apartment listing monitoring.
# It verifies that new listings are detected while previously
# seen listings are not reported as new.

from app.models import Listing
from app.monitoring import ApartmentListingMonitor
from app.sources.base import ApartmentSource
from app.storage.base import ListingRepository
from app.models import Listing
from app.monitoring.monitor import ApartmentListingMonitor
from app.storage.sqlite import SQLiteListingRepository


class FakeSource(ApartmentSource):
    """Test source that returns predefined listings."""

    name = "fake"

    def __init__(self, listings: list[Listing]):
        self.listings = listings

    def fetch_listings(self) -> list[Listing]:
        return self.listings


class FakeRepository(ListingRepository):
    """In-memory repository used for testing."""

    def __init__(self):
        self.listings: dict[tuple[str, str], Listing] = {}

    def save(self, listing: Listing) -> None:
        key = (listing.source, listing.listing_id)

        if key in self.listings:
            listing.first_seen_at = self.listings[key].first_seen_at

        self.listings[key] = listing

    def get(self, source: str, listing_id: str) -> Listing | None:
        return self.listings.get((source, listing_id))

    def get_all(self) -> list[Listing]:
        return list(self.listings.values())


def test_monitor_detects_new_listing():

    listing = Listing(
        source="fake",
        listing_id="123",
        url="https://example.com/123",
    )

    source = FakeSource([listing])
    repository = FakeRepository()

    monitor = ApartmentListingMonitor(
        source=source,
        repository=repository,
    )

    new_listings = monitor.check()

    assert new_listings == [listing]


def test_monitor_does_not_report_existing_listing():

    listing = Listing(
        source="fake",
        listing_id="123",
        url="https://example.com/123",
    )

    source = FakeSource([listing])
    repository = FakeRepository()

    monitor = ApartmentListingMonitor(
        source=source,
        repository=repository,
    )

    first_check = monitor.check()
    second_check = monitor.check()

    assert len(first_check) == 1
    assert len(second_check) == 0

def test_bootstrap_stores_existing_listings_without_alerting(tmp_path):
    repository = SQLiteListingRepository(
        str(tmp_path / "listings.db")
    )

    listing = Listing(
        source="fake",
        listing_id="123",
        url="https://example.com/apartment/123",
    )

    source = FakeSource([listing])

    monitor = ApartmentListingMonitor(
        source=source,
        repository=repository,
    )

    monitor.bootstrap()

    assert repository.get("fake", "123") is not None
    assert monitor.check() == []