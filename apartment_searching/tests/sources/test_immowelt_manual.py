# This file manually tests the Immowelt browser client.
# It opens the configured Immowelt search page and prints
# the actual result order and sorting controls.

from app.config import load_settings
from app.sources.immowelt import ImmoweltClient


def main() -> None:
    settings = load_settings()

    client = ImmoweltClient(
        url=settings.immowelt_url,
        headless=False,
    )

    try:
        client.start()

        client.wait_for_listings()

        print()
        print(
            f"[IMMOWELT] "
            f"{client.count_listing_cards()} listing cards detected."
        )

        client.debug_sorting_controls()

        client.debug_listings(limit=25)

        client.save_debug_files()

        print()
        print(
            "[IMMOWELT] Browser remains open."
        )

        input(
            "Inspect the result order in the browser, "
            "then press Enter to close..."
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()