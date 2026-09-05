# This file performs a manual email delivery test.
# It sends one test email through Resend to verify
# that the configured email credentials work.

from app.config import load_settings
from app.models import Listing
from app.notifications.email import EmailNotificationService


def main() -> None:
    """Send one test email."""

    settings = load_settings()

    service = EmailNotificationService(
        api_key=settings.email_api_key,
        sender=settings.email_from,
        recipient=settings.notification_recipient,
    )

    service.send_new_listings(
        [
            Listing(
                source="test",
                listing_id="TEST-001",
                url="https://example.com/apartment",
            )
        ]
    )

    print("Test email sent.")


if __name__ == "__main__":
    main()