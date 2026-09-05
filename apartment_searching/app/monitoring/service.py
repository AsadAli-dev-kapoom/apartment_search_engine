# This file coordinates apartment monitoring and notifications.
# It runs a monitoring check and sends notifications for newly discovered listings.

from app.monitoring.base import ListingMonitor
from app.notifications.base import NotificationService


class MonitoringService:
    """Run monitoring checks and notify about new listings."""

    def __init__(
        self,
        monitor: ListingMonitor,
        notification_service: NotificationService,
    ):
        self.monitor = monitor
        self.notification_service = notification_service

    def check(self) -> None:
        """Check for new listings and notify when any are found."""

        print("[MONITOR] Checking for listings...")

        new_listings = self.monitor.check()

        print(
            f"[MONITOR] Found {len(new_listings)} new listing(s)."
        )

        if new_listings:
            print("[MONITOR] Sending email notification...")

            self.notification_service.send_new_listings(
                new_listings
            )

            print("[MONITOR] Email notification sent.")