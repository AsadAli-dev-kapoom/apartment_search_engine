# This file handles browser interaction with ImmoScout24.
# It opens the configured ImmoScout24 search page and waits for
# apartment results to become available.
# It does not parse listings, store data, or send notifications.

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


class ImmoScoutClient:
    """Browser client for the ImmoScout24 apartment search."""

    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.headless = headless

        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> None:
        """Start the browser and open the ImmoScout24 search."""

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless
        )

        self._context = self._browser.new_context()

        self._page = self._context.new_page()

        print("[IMMOSCOUT] Opening apartment search...")

        self._page.goto(
            self.url,
            wait_until="domcontentloaded",
        )

    def wait_for_listings(self, timeout: int = 120) -> None:
        """Wait for ImmoScout24 listings after manual bot verification."""

        if self._page is None:
            raise RuntimeError("ImmoScoutClient has not been started.")

        print("[IMMOSCOUT] Waiting for apartment listings...")
        print(f"[IMMOSCOUT] Current URL: {self._page.url}")

        print(
            "[IMMOSCOUT] If a bot verification is shown, "
            "complete it manually in the browser."
        )

        self._page.locator(
            'a[href*="/expose/"]'
        ).first.wait_for(
            state="visible",
            timeout=timeout * 1000,
        )

        print("[IMMOSCOUT] Apartment listings detected.")

        self._page.screenshot(
            path="logs/immoscout-debug.png",
            full_page=True,
        )

        print(
            "[IMMOSCOUT] Debug screenshot saved to "
            "logs/immoscout-debug.png"
        )
    
    @property
    def page(self) -> Page:
        """Return the current Playwright page."""

        if self._page is None:
            raise RuntimeError("ImmoScoutClient has not been started.")

        return self._page

    def close(self) -> None:
        """Close the browser and release Playwright resources."""

        if self._context:
            self._context.close()

        if self._browser:
            self._browser.close()

        if self._playwright:
            self._playwright.stop()