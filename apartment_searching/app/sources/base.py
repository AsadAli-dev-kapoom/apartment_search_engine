# This file defines the common interface that every apartment website must implement.
# It allows the monitoring system to work with SAGA, Immowelt, ImmoScout, etc. in the same way.

from abc import ABC, abstractmethod

from app.models import Listing


class ApartmentSource(ABC):
    """Base interface for all apartment sources."""

    name: str

    @abstractmethod
    def fetch_listings(self) -> list[Listing]:
        """Return all currently available listings."""
        raise NotImplementedError