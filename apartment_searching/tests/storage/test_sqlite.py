# This file tests the SQLite listing repository.
# It verifies that listings can be stored, retrieved,
# and tracked over multiple observations.

import time

from app.models import Listing
from app.storage.sqlite import SQLiteListingRepository


def test_sqlite_repository_saves_and_gets_listing(tmp_path):

    database_path = tmp_path / "listings.db"

    repository = SQLiteListingRepository(str(database_path))

    listing = Listing(
        source="saga",
        listing_id="6783",
        url="https://www.saga.hamburg/immo-detail/6783/test-apartment",
    )

    repository.save(listing)

    stored = repository.get("saga", "6783")

    assert stored is not None
    assert stored.source == "saga"
    assert stored.listing_id == "6783"
    assert stored.url == listing.url
    assert stored.first_seen_at is not None
    assert stored.last_seen_at is not None


def test_sqlite_repository_returns_none_for_unknown_listing(tmp_path):

    database_path = tmp_path / "listings.db"

    repository = SQLiteListingRepository(str(database_path))

    assert repository.get("saga", "9999") is None


def test_first_seen_does_not_change(tmp_path):

    database_path = tmp_path / "listings.db"

    repository = SQLiteListingRepository(str(database_path))

    listing = Listing(
        source="saga",
        listing_id="6783",
        url="https://www.saga.hamburg/immo-detail/6783/test-apartment",
    )

    repository.save(listing)

    first = repository.get("saga", "6783")

    assert first is not None
    assert first.first_seen_at is not None
    assert first.last_seen_at is not None

    first_seen = first.first_seen_at
    first_last_seen = first.last_seen_at

    time.sleep(0.01)

    repository.save(listing)

    second = repository.get("saga", "6783")

    assert second is not None

    assert second.first_seen_at == first_seen
    assert second.last_seen_at is not None
    assert second.last_seen_at > first_last_seen