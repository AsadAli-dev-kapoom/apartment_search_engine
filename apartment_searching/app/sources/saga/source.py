# This file implements the SAGA apartment source.
# It keeps the SAGA browser session alive so repeated monitoring checks
# can reuse the same session instead of reopening the website each time.

from app.models import Listing
from app.sources.base import ApartmentSource

from .client import SagaClient
from .parser import SagaParser


class SagaSource(ApartmentSource):
    """SAGA Hamburg apartment source."""

    name = "saga"

    def __init__(
        self,
        url: str,
        headless: bool = False,
    ):
        self.client = SagaClient(
            url=url,
            headless=headless,
        )
        self.parser = SagaParser()
        self._started = False

    def start(self) -> None:
        """Start the browser session."""

        if self._started:
            return

        self.client.start()
        self.client.wait_for_listings()

        self._started = True

    def fetch_listings(self) -> list[Listing]:
        """Fetch listings using the existing browser session."""

        print("[SAGA] Fetching listings...")

        if not self._started:
            self.start()

        listings = self.parser.parse(self.client.page)

        print(f"[SAGA] Parsed {len(listings)} listing(s).")

        return listings

    def close(self) -> None:
        """Close the browser session."""

        if not self._started:
            return

        self.client.close()
        self._started = False