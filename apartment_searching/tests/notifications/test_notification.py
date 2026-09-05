# This file tests the notification interface.
# It verifies that notification providers must implement
# the required new-listing notification operation.

from app.notifications import NotificationService


def test_notification_service_is_abstract():

    assert NotificationService.__abstractmethods__ == {
        "send_new_listings",
    }