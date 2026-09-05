# This file defines the common monitoring interface.
# It coordinates apartment sources and storage to detect new listings.

from abc import ABC, abstractmethod

from app.models import Listing


class ListingMonitor(ABC):
    """Base interface for listing monitoring."""

    @abstractmethod
    def check(self) -> list[Listing]:
        """Check a source and return newly discovered listings."""
        raise NotImplementedError