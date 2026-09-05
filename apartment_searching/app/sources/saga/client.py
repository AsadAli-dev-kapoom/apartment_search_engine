# This file handles browser interaction with the SAGA website.
# It opens the configured SAGA apartment search page and waits for
# the page to become available after any required manual CAPTCHA verification.
# It does not parse listings, store data, or send notifications.

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


class SagaClient:
    """Browser client for the SAGA apartment search."""

    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.headless = headless

        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def start(self) -> None:
        """Start the browser and open the SAGA apartment search."""

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless
        )

        self._context = self._browser.new_context()
        self._page = self._context.new_page()

        self._page.goto(self.url)

    def wait_for_listings(self, timeout: int = 1000) -> None:
        """Wait until SAGA apartment cards appear."""

        if self._page is None:
            raise RuntimeError("SagaClient has not been started.")

        print("[SAGA] Waiting for apartment listings...")
        print(f"[SAGA] Current URL: {self._page.url}")

        self._page.wait_for_timeout(5000)

        print(f"[SAGA] Page title: {self._page.title()}")

        self._page.screenshot(
            path="logs/saga-debug.png",
            full_page=True,
        )

        print("[SAGA] Debug screenshot saved to logs/saga-debug.png")

        self._page.locator(
            '[id^="APARTMENT-card-"]'
        ).first.wait_for(
            state="visible",
            timeout=timeout * 1000,
        )

        print("[SAGA] Apartment listings detected.")

    
    @property
    def page(self) -> Page:
        """Return the current Playwright page."""

        if self._page is None:
            raise RuntimeError("SagaClient has not been started.")

        return self._page

    def close(self) -> None:
        """Close the browser and release Playwright resources."""

        if self._context:
            self._context.close()

        if self._browser:
            self._browser.close()

        if self._playwright:
            self._playwright.stop()