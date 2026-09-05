# This file defines the common storage interface.
# It allows the application to store listings without depending
# on a specific database or storage implementation.

from abc import ABC, abstractmethod

from app.models import Listing


class ListingRepository(ABC):
    """Base interface for storing apartment listings."""

    @abstractmethod
    def save(self, listing: Listing) -> None:
        """Store or update a listing."""
        raise NotImplementedError

    @abstractmethod
    def get(self, source: str, listing_id: str) -> Listing | None:
        """Return a listing by source and ID."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[Listing]:
        """Return all stored listings."""
        raise NotImplementedError