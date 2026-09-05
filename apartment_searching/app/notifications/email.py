# This file implements email notifications using Resend.
# It sends newly discovered apartment listings through the Resend API.
# It does not contain email credentials; those are supplied through configuration.

import resend

from app.models import Listing
from app.notifications.base import NotificationService


class EmailNotificationService(NotificationService):
    """Send apartment alerts by email using Resend."""

    def __init__(
        self,
        api_key: str,
        sender: str,
        recipient: str,
    ):
        self.api_key = api_key
        self.sender = sender
        self.recipient = recipient

    def send_new_listings(self, listings: list[Listing]) -> None:
        """Send an email containing newly discovered listings."""

        if not listings:
            return

        resend.api_key = self.api_key

        resend.Emails.send(
            {
                "from": self.sender,
                "to": [self.recipient],
                "subject": (
                    f"Apartment Search: "
                    f"{len(listings)} new listing(s)"
                ),
                "text": self._build_body(listings),
            }
        )

    @staticmethod
    def _build_body(listings: list[Listing]) -> str:
        """Build the email body from listings."""

        lines = [
            "New apartment listing(s):",
            "",
        ]

        for listing in listings:
            lines.append(f"Source: {listing.source}")
            lines.append(f"ID: {listing.listing_id}")
            lines.append(f"URL: {listing.url}")
            lines.append("")

        return "\n".join(lines)