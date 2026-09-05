# This file tests application configuration.
# It verifies that configuration can be loaded correctly
# when environment variables are not provided.

from app.config import load_settings


def test_load_settings_defaults(monkeypatch):

    monkeypatch.delenv("SAGA_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("MONITORING_INTERVAL_SECONDS", raising=False)
    monkeypatch.delenv("EMAIL_API_KEY", raising=False)
    monkeypatch.delenv("EMAIL_FROM", raising=False)
    monkeypatch.delenv("NOTIFICATION_RECIPIENT", raising=False)

    settings = load_settings()

    assert settings.saga_url == (
        "https://www.saga.hamburg/immobiliensuche?Kategorie=APARTMENT"
    )

    assert settings.database_path == "data/listings.db"
    assert settings.monitoring_interval_seconds == 300

    assert settings.email_api_key == ""
    assert settings.email_from == "onboarding@resend.dev"
    assert settings.notification_recipient == (
        "asad.aliappartment@hotmail.com"
    )