# This file tests the email notification service.
# It verifies that listing information is correctly converted
# into an email without making a real SMTP connection.

import smtplib

from app.models import Listing
from app.notifications.email import EmailNotificationService


def test_email_body_contains_listing_information():

    listing = Listing(
        source="saga",
        listing_id="6783",
        url="https://www.saga.hamburg/immo-detail/6783/test-apartment",
    )

    service = EmailNotificationService(
        api_key="test-api-key",
        sender="onboarding@resend.dev",
        recipient="test@example.com",
    )

    body = service._build_body([listing])

    assert "saga" in body
    assert "6783" in body
    assert listing.url in body


def test_empty_listing_list_does_not_send(monkeypatch):

    service = EmailNotificationService(
        api_key="test-api-key",
        sender="onboarding@resend.dev",
        recipient="test@example.com",
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("SMTP should not be called")

    monkeypatch.setattr(smtplib, "SMTP", fail_if_called)

    service.send_new_listings([])