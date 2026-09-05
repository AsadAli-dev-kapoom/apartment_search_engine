from __future__ import annotations

import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


# =============================================================================
# CONFIGURATION
# =============================================================================

SAGA_URL = (
    "https://www.saga.hamburg/"
    "immobiliensuche?Kategorie=APARTMENT"
)

BASE_URL = "https://www.saga.hamburg"

EMAIL_TO = "asad.aliappartment@hotmail.com"

EMAIL_FROM = os.getenv("SAGA_EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("SAGA_EMAIL_PASSWORD")

SMTP_HOST = os.getenv(
    "SAGA_SMTP_HOST",
    "smtp-mail.outlook.com",
)

SMTP_PORT = int(
    os.getenv(
        "SAGA_SMTP_PORT",
        "587",
    )
)

# Maximum time to wait for the CAPTCHA + SAGA listing request.
MAX_WAIT_SECONDS = 600


# =============================================================================
# LISTING ID
# =============================================================================


def extract_listing_id(url: str) -> str | None:
    """
    Extract the numeric SAGA listing ID.

    Example:
        /immo-detail/6774/...
        -> 6774
    """

    match = re.search(
        r"/immo-detail/(\d+)(?:/|$)",
        url,
    )

    if match:
        return match.group(1)

    return None


# =============================================================================
# LISTING CARDS
# =============================================================================


def find_listing_cards(page):
    """
    Actual SAGA apartment card selector.
    """

    return page.locator(
        '[id^="APARTMENT-card-"]'
    )


def get_listing_ids(page) -> list[str]:
    """
    Extract ONLY numeric SAGA listing IDs.
    """

    cards = find_listing_cards(page)

    ids: list[str] = []

    for index in range(cards.count()):

        card = cards.nth(index)

        links = card.locator(
            'a[href*="/immo-detail/"]'
        )

        if links.count() == 0:
            continue

        href = links.first.get_attribute(
            "href"
        )

        if not href:
            continue

        url = urljoin(
            BASE_URL,
            href,
        )

        listing_id = extract_listing_id(
            url
        )

        if listing_id:
            ids.append(listing_id)

    # Remove duplicates while preserving order.
    return list(
        dict.fromkeys(ids)
    )


# =============================================================================
# EMAIL
# =============================================================================


def send_email(ids: list[str]) -> None:
    """
    Send an email containing ONLY the apartment IDs.
    """

    if not EMAIL_FROM:
        raise RuntimeError(
            "SAGA_EMAIL_FROM is not configured."
        )

    if not EMAIL_PASSWORD:
        raise RuntimeError(
            "SAGA_EMAIL_PASSWORD is not configured."
        )

    message = EmailMessage()

    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = "SAGA Apartment IDs"

    # IMPORTANT:
    # Email body contains IDs ONLY.
    message.set_content(
        "\n".join(ids)
    )

    print()
    print("=" * 70)
    print("SENDING EMAIL")
    print("=" * 70)

    print(
        f"[→] Sending {len(ids)} ID(s) "
        f"to {EMAIL_TO}..."
    )

    context = ssl.create_default_context()

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30,
    ) as smtp:

        smtp.ehlo()

        smtp.starttls(
            context=context
        )

        smtp.ehlo()

        smtp.login(
            EMAIL_FROM,
            EMAIL_PASSWORD,
        )

        smtp.send_message(
            message
        )

    print(
        "[✓] Email sent."
    )


# =============================================================================
# MAIN
# =============================================================================


def main():

    print()
    print("=" * 70)
    print("SAGA → EMAIL ID MONITOR")
    print("=" * 70)

    print()
    print(
        f"Recipient: {EMAIL_TO}"
    )

    # -------------------------------------------------------------------------
    # Playwright
    # -------------------------------------------------------------------------

    with sync_playwright() as playwright:

        browser = None
        context = None

        try:

            print()
            print(
                "[→] Starting Chromium..."
            )

            browser = playwright.chromium.launch(
                headless=False,
            )

            context = browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 1000,
                }
            )

            page = context.new_page()

            # -----------------------------------------------------------------
            # IMPORTANT:
            #
            # Listen for SAGA's follow-up HTTP request BEFORE opening SAGA.
            #
            # Initial request:
            #     401
            #
            # After CAPTCHA:
            #     SAGA's JavaScript fetches the search page again
            #     and normally gets 200.
            # -----------------------------------------------------------------

            saga_successful_response = False

            def handle_response(response):

                nonlocal saga_successful_response

                try:

                    response_url = response.url

                    # Same search URL.
                    same_url = (
                        response_url.split("#")[0]
                        == SAGA_URL
                    )

                    if (
                        same_url
                        and response.status == 200
                    ):

                        print()
                        print(
                            "[✓] SAGA returned HTTP 200."
                        )

                        print(
                            "[→] This indicates that "
                            "the post-CAPTCHA request completed."
                        )

                        saga_successful_response = True

                except Exception:
                    pass

            page.on(
                "response",
                handle_response,
            )

            # -----------------------------------------------------------------
            # OPEN SAGA
            # -----------------------------------------------------------------

            print()
            print(
                "[→] Opening SAGA..."
            )

            try:

                response = page.goto(
                    SAGA_URL,
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )

                if response:

                    print(
                        f"[→] Initial HTTP status: "
                        f"{response.status}"
                    )

            except Exception as exc:

                print()
                print(
                    f"[!] Navigation warning: {exc}"
                )

            # -----------------------------------------------------------------
            # WAIT FOR CAPTCHA
            # -----------------------------------------------------------------

            print()
            print(
                "[→] Waiting for Friendly CAPTCHA..."
            )

            print()
            print(
                ">>> Complete the CAPTCHA manually "
                "in Chromium."
            )

            print(
                ">>> DO NOT press anything in the terminal."
            )

            print(
                ">>> Python will detect completion automatically."
            )

            print()

            # -----------------------------------------------------------------
            # AUTOMATIC DETECTION LOOP
            # -----------------------------------------------------------------

            for second in range(
                1,
                MAX_WAIT_SECONDS + 1,
            ):

                # -------------------------------------------------------------
                # First check: SAGA's post-CAPTCHA 200 response.
                # -------------------------------------------------------------

                if saga_successful_response:

                    print()
                    print(
                        "[→] Post-CAPTCHA SAGA response detected."
                    )

                # -------------------------------------------------------------
                # Second check: actual apartment cards.
                #
                # This is the definitive condition.
                # -------------------------------------------------------------

                ids = get_listing_ids(
                    page
                )

                if ids:

                    print()
                    print("=" * 70)
                    print("APARTMENT LISTINGS DETECTED")
                    print("=" * 70)

                    print()

                    for listing_id in ids:
                        print(
                            listing_id
                        )

                    # ---------------------------------------------------------
                    # EMAIL
                    # ---------------------------------------------------------

                    send_email(
                        ids
                    )

                    print()
                    print("=" * 70)
                    print("SUCCESS")
                    print("=" * 70)

                    print()
                    print(
                        "IDs sent:"
                    )

                    print(
                        "\n".join(ids)
                    )

                    print()

                    return

                # -------------------------------------------------------------
                # Progress
                # -------------------------------------------------------------

                if second % 5 == 0:

                    print(
                        f"[→] Waiting... "
                        f"{second}/{MAX_WAIT_SECONDS}s "
                        f"| SAGA 200: "
                        f"{saga_successful_response} "
                        f"| IDs: 0"
                    )

                page.wait_for_timeout(
                    1_000
                )

            # -----------------------------------------------------------------
            # TIMEOUT
            # -----------------------------------------------------------------

            print()
            print("=" * 70)
            print("TIMEOUT")
            print("=" * 70)

            print()
            print(
                "CAPTCHA may have been completed, "
                "but no apartment cards were detected."
            )

            print()
            print(
                f"Current URL: {page.url}"
            )

            print(
                f"SAGA 200 detected: "
                f"{saga_successful_response}"
            )

            print()
            print(
                "Chromium will remain open for inspection."
            )

            print(
                "Close it manually when finished."
            )

            input()

        except KeyboardInterrupt:

            print()
            print(
                "[!] Stopped by user."
            )

        except Exception as exc:

            print()
            print("=" * 70)
            print("ERROR")
            print("=" * 70)

            print()
            print(
                repr(exc)
            )

            print()
            print(
                "Chromium will remain open."
            )

            try:
                input()
            except EOFError:
                pass

        finally:

            if context:

                try:
                    context.close()
                except Exception:
                    pass

            if browser:

                try:
                    browser.close()
                except Exception:
                    pass


if __name__ == "__main__":
    main()