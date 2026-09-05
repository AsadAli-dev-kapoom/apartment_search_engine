# This file tests the monitoring service.
# It verifies that newly discovered listings are passed
# to the notification service.

from app.models import Listing
from app.monitoring import MonitoringService
from app.monitoring.base import ListingMonitor
from app.notifications.base import NotificationService


class FakeMonitor(ListingMonitor):
    """Test monitor returning predefined listings."""

    def __init__(self, listings):
        self.listings = listings

    def check(self):
        return self.listings


class FakeNotificationService(NotificationService):
    """Test notification service recording notifications."""

    def __init__(self):
        self.notifications = []

    def send_new_listings(self, listings):
        self.notifications.append(listings)


def test_new_listings_are_sent_to_notification_service():

    listing = Listing(
        source="saga",
        listing_id="6783",
        url="https://www.saga.hamburg/immo-detail/6783/test-apartment",
    )

    monitor = FakeMonitor([listing])
    notification_service = FakeNotificationService()

    service = MonitoringService(
        monitor=monitor,
        notification_service=notification_service,
    )

    service.check()

    assert notification_service.notifications == [[listing]]


def test_no_notification_when_no_new_listings():

    monitor = FakeMonitor([])
    notification_service = FakeNotificationService()

    service = MonitoringService(
        monitor=monitor,
        notification_service=notification_service,
    )

    service.check()

    assert notification_service.notifications == []