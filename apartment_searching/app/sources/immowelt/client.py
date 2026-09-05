# This file handles browser interaction with Immowelt.
# It opens the configured search page, waits for apartment listings,
# and provides diagnostics for determining Immowelt's result ordering.
# It does not parse listings, store data, or send notifications.

from pathlib import Path

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)


class ImmoweltClient:
    """Browser client for the Immowelt apartment search."""

    LISTING_CARD_SELECTOR = (
        '[data-testid="serp-core-classified-card-testid"]'
    )

    LISTING_LINK_SELECTOR = (
        'a[data-testid="card-mfe-covering-link-testid"]'
    )

    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.headless = headless

        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> None:
        """Start Playwright and open the Immowelt search page."""

        if self._page is not None:
            return

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
        )

        self._context = self._browser.new_context()

        self._page = self._context.new_page()

        print("[IMMOWELT] Opening apartment search...")
        print(f"[IMMOWELT] URL: {self.url}")

        self._page.goto(
            self.url,
            wait_until="domcontentloaded",
        )

        print(
            f"[IMMOWELT] Current URL: {self._page.url}"
        )

    def wait_for_listings(self, timeout: int = 120) -> None:
        """Wait until Immowelt apartment cards are visible."""

        page = self.page

        print("[IMMOWELT] Waiting for apartment listings...")

        try:
            page.locator(
                self.LISTING_CARD_SELECTOR
            ).first.wait_for(
                state="visible",
                timeout=timeout * 1000,
            )

        except Exception as exc:
            print(
                "[IMMOWELT] Apartment listings were not detected."
            )

            print(
                f"[IMMOWELT] Current URL: {page.url}"
            )

            print(
                f"[IMMOWELT] Page title: {page.title()}"
            )

            self.save_debug_files()

            raise RuntimeError(
                "Immowelt apartment listings were not detected. "
                "Debug files were saved under logs/."
            ) from exc

        print("[IMMOWELT] Apartment listings detected.")

    def get_listing_cards(self):
        """Return the currently rendered Immowelt listing cards."""

        return self.page.locator(
            self.LISTING_CARD_SELECTOR
        )

    def count_listing_cards(self) -> int:
        """Return the number of currently rendered listing cards."""

        return self.get_listing_cards().count()

    def debug_listings(self, limit: int | None = None) -> None:
        """
        Print the current listing order.

        This is diagnostic functionality used while developing
        the Immowelt parser.
        """

        cards = self.get_listing_cards()

        count = cards.count()

        if limit is not None:
            count = min(count, limit)

        print()
        print("=" * 70)
        print("IMMOWELT CURRENT RESULT ORDER")
        print("=" * 70)

        for index in range(count):
            card = cards.nth(index)

            link = card.locator(
                self.LISTING_LINK_SELECTOR
            ).first

            listing_id = card.get_attribute("id")

            href = None

            if link.count() > 0:
                href = link.get_attribute("href")

            title = None

            if link.count() > 0:
                title = link.get_attribute("title")

            print()
            print(f"[{index + 1}]")
            print(f"  Card ID: {listing_id}")
            print(f"  URL:     {href}")
            print(f"  Title:   {title}")

    def debug_sorting_controls(self) -> None:
        """
        Print visible controls whose text may relate to sorting.

        We inspect the actual DOM instead of assuming a selector.
        """

        page = self.page

        print()
        print("=" * 70)
        print("IMMOWELT SORTING CONTROLS")
        print("=" * 70)

        candidates = page.locator(
            "button, [role='button'], select, option"
        )

        found = 0

        for index in range(candidates.count()):
            element = candidates.nth(index)

            try:
                if not element.is_visible():
                    continue

                text = element.inner_text().strip()

                if not text:
                    continue

                lowered = text.lower()

                if any(
                    word in lowered
                    for word in (
                        "sort",
                        "neu",
                        "aktuell",
                        "relevant",
                        "preis",
                        "datum",
                    )
                ):
                    print(
                        f"  {element.evaluate('(e) => e.outerHTML')}"
                    )

                    found += 1

            except Exception:
                continue

        if found == 0:
            print(
                "  No obvious sorting control found."
            )

    def save_debug_files(
        self,
        directory: str = "logs",
    ) -> None:
        """Save HTML, visible text and screenshot."""

        page = self.page

        output_dir = Path(directory)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        html_path = (
            output_dir / "immowelt-page.html"
        )

        text_path = (
            output_dir / "immowelt-page.txt"
        )

        screenshot_path = (
            output_dir / "immowelt-debug.png"
        )

        html_path.write_text(
            page.content(),
            encoding="utf-8",
        )

        text_path.write_text(
            page.locator("body").inner_text(),
            encoding="utf-8",
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        print()
        print("[IMMOWELT] Debug files saved:")
        print(f"  {html_path}")
        print(f"  {text_path}")
        print(f"  {screenshot_path}")

    @property
    def page(self) -> Page:
        """Return the active Immowelt page."""

        if self._page is None:
            raise RuntimeError(
                "ImmoweltClient has not been started."
            )

        return self._page

    def close(self) -> None:
        """Close the browser and Playwright."""

        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

        self._page = None