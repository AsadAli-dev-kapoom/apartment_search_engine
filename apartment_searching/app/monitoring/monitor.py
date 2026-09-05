# This file implements listing monitoring.
# It compares current listings from a source with stored listings
# and returns only listings that have not been seen before.
# It also supports an initial bootstrap that stores existing listings
# without treating them as new alerts.

from app.models import Listing
from app.monitoring.base import ListingMonitor
from app.sources.base import ApartmentSource
from app.storage.base import ListingRepository


class ApartmentListingMonitor(ListingMonitor):
    """Monitor an apartment source for new listings."""

    def __init__(
        self,
        source: ApartmentSource,
        repository: ListingRepository,
    ):
        self.source = source
        self.repository = repository

    def check(self) -> list[Listing]:
        """Fetch current listings and return newly discovered ones."""

        current_listings = self.source.fetch_listings()

        new_listings: list[Listing] = []

        for listing in current_listings:
            existing = self.repository.get(
                listing.source,
                listing.listing_id,
            )

            if existing is None:
                self.repository.save(listing)
                new_listings.append(listing)
            else:
                self.repository.save(listing)

        return new_listings

    def bootstrap(self) -> None:
        """Store all currently available listings without alerts."""

        current_listings = self.source.fetch_listings()

        for listing in current_listings:
            self.repository.save(listing)