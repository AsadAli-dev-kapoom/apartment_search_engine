# This file parses the SAGA apartment search page.
# It extracts apartment IDs and URLs and converts them into
# the common Listing model.
# It does not open browsers, monitor changes, store data, or send notifications.

from playwright.sync_api import Page

from app.models import Listing


class SagaParser:
    """Parser for SAGA apartment listings."""

    SOURCE_NAME = "saga"

    def parse(self, page: Page) -> list[Listing]:
        """Extract all apartment listings from the current SAGA page."""

        listings: list[Listing] = []

        cards = page.locator('[id^="APARTMENT-card-"]')

        for i in range(cards.count()):
            card = cards.nth(i)

            listing_id = self._extract_listing_id(card)

            if listing_id is None:
                continue

            url = self._extract_url(card)

            if url is None:
                continue

            listings.append(
                Listing(
                    source=self.SOURCE_NAME,
                    listing_id=listing_id,
                    url=url,
                )
            )

        return listings

    def _extract_listing_id(self, card) -> str | None:
        """Extract the SAGA listing ID from an apartment card."""

        link = card.locator("h3 a").first

        if link.count() == 0:
            return None

        href = link.get_attribute("href")

        if not href:
            return None

        # Expected format:
        # /immo-detail/6783/...
        parts = href.split("/")

        try:
            detail_index = parts.index("immo-detail")
            return parts[detail_index + 1]
        except (ValueError, IndexError):
            return None

    def _extract_url(self, card) -> str | None:
        """Extract the complete SAGA apartment URL."""

        link = card.locator("h3 a").first

        if link.count() == 0:
            return None

        href = link.get_attribute("href")

        if not href:
            return None

        if href.startswith("http"):
            return href

        return f"https://www.saga.hamburg{href}"