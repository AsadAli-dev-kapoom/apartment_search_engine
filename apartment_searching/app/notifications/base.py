# This file defines the common notification interface.
# It allows the application to send listing alerts through
# different notification providers without changing the monitor.

from abc import ABC, abstractmethod

from app.models import Listing


class NotificationService(ABC):
    """Base interface for notification providers."""

    @abstractmethod
    def send_new_listings(self, listings: list[Listing]) -> None:
        """Send notifications for newly discovered listings."""
        raise NotImplementedError