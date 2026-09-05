from app.config import load_settings
from app.sources.immoscout.client import ImmoScoutClient


def main():
    settings = load_settings()

    client = ImmoScoutClient(
        url=settings.immoscout_url,
        headless=False,
    )

    try:
        client.start()
        client.wait_for_listings()

        print("[TEST] ImmoScout24 page loaded successfully.")

        input("[TEST] Press Enter to close the browser...")

    finally:
        client.close()


if __name__ == "__main__":
    main()