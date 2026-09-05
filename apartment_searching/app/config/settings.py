# This file defines application configuration.
# It loads runtime settings from environment variables and the .env file.
# Secrets such as the email API key are kept outside the application source code.

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    """Application configuration."""

    saga_url: str
    immoscout_url: str
    immowelt_url: str
    database_path: str
    monitoring_interval_seconds: int

    email_api_key: str
    email_from: str
    notification_recipient: str
    # bootstrap_mode: bool


def load_settings() -> Settings:
    """Load application settings from environment variables."""

    return Settings(
        saga_url=os.getenv(
            "SAGA_URL",
            "https://www.saga.hamburg/immobiliensuche?Kategorie=APARTMENT",
        ),
        immoscout_url=os.getenv(
            "IMMOSCOUT_URL",
            "https://www.immobilienscout24.de/Suche/de/hamburg/hamburg/wohnung-mieten?price=-1014.0&pricetype=calculatedtotalrent&sorting=2&enteredFrom=result_list",
        ),
        immowelt_url=os.getenv(
            "IMMOWELT_URL",
            "https://www.immowelt.de/suche/mieten/wohnung/hamburg/hamburg-20095/ad08de1113",
        ),
        database_path=os.getenv(
            "DATABASE_PATH",
            "data/listings.db",
        ),
        monitoring_interval_seconds=int(
            os.getenv("MONITORING_INTERVAL_SECONDS", "300")
        ),
        email_api_key=os.getenv("EMAIL_API_KEY", ""),
        email_from=os.getenv(
            "EMAIL_FROM",
            "onboarding@resend.dev",
        ),
        notification_recipient=os.getenv(
            "NOTIFICATION_RECIPIENT",
            "asad.aliappartment@hotmail.com",
        ),
        # bootstrap_mode=os.getenv(
        #     "BOOTSTRAP_MODE",
        #     "false",
        # ).lower() == "true",
    )