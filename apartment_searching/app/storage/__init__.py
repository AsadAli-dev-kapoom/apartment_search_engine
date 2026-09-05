# This file exposes the common storage interface.
# It allows the application to import the repository contract
# without depending on a specific storage implementation.

from .base import ListingRepository

__all__ = ["ListingRepository"]