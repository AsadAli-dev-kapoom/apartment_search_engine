from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import (
    Page,
    Request,
    Response,
    sync_playwright,
)


# ============================================================
# Configuration
# ============================================================

SAGA_URL = (
    "https://www.saga.hamburg/"
    "immobiliensuche?Kategorie=APARTMENT"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS_DIR = PROJECT_ROOT / "data" / "inspection"

SCREENSHOT_PATH = ARTIFACTS_DIR / "saga-page-after-verification.png"
HTML_PATH = ARTIFACTS_DIR / "saga-page-after-verification.html"
NETWORK_PATH = ARTIFACTS_DIR / "network-after-verification.json"
SUMMARY_PATH = ARTIFACTS_DIR / "summary-after-verification.json"


# ============================================================
# Helpers
# ============================================================

def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_directories() -> None:
    ARTIFACTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# Network inspection
# ============================================================

def request_info(request: Request) -> dict:
    return {
        "method": request.method,
        "url": request.url,
        "resource_type": request.resource_type,
        "is_navigation": request.is_navigation_request(),
        "headers": {
            key: value
            for key, value in request.headers.items()
            if key.lower()
            in {
                "content-type",
                "accept",
                "origin",
                "referer",
            }
        },
    }


def response_info(response: Response) -> dict:
    request = response.request

    return {
        "status": response.status,
        "status_text": response.status_text,
        "url": response.url,
        "resource_type": request.resource_type,
        "content_type": response.headers.get(
            "content-type",
            "",
        ),
    }


# ============================================================
# Page inspection
# ============================================================

def get_page_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(
            timeout=10_000
        )
    except Exception:
        return ""


def inspect_page(page: Page) -> dict:

    title = page.title()
    url = page.url
    text = get_page_text(page)

    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(a => ({
            text: (a.innerText || "").trim(),
            href: a.href
        }))
        """
    )

    forms = page.locator("form").evaluate_all(
        """
        elements => elements.map(form => ({
            action: form.action,
            method: form.method,
            text: (form.innerText || "").trim()
        }))
        """
    )

    return {
        "title": title,
        "url": url,
        "text_length": len(text),
        "text_preview": text[:20_000],
        "links": links,
        "forms": forms,
    }


# ============================================================
# Verification detection
# ============================================================

def detect_verification(page: Page) -> dict:

    text = get_page_text(page).lower()

    indicators = [
        "captcha",
        "ich bin ein mensch",
        "verify you are human",
        "verify that you are human",
        "security check",
        "sicherheitsprüfung",
        "access denied",
        "unusual traffic",
        "cloudflare",
    ]

    matches = [
        indicator
        for indicator in indicators
        if indicator in text
    ]

    return {
        "detected": bool(matches),
        "indicators": matches,
    }


# ============================================================
# Listing candidate detection
# ============================================================

def find_listing_candidates(page: Page) -> list[dict]:

    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(a => ({
            text: (a.innerText || "").trim(),
            href: a.href
        }))
        """
    )

    candidates = []

    patterns = [
        r"wohnung",
        r"apartment",
        r"immobil",
        r"expose",
        r"angebot",
        r"object",
        r"detail",
        r"miete",
    ]

    for link in links:

        text = link.get("text", "")
        href = link.get("href", "")

        combined = f"{text} {href}".lower()

        if any(
            re.search(pattern, combined)
            for pattern in patterns
        ):
            candidates.append(link)

    return candidates


# ============================================================
# Human verification
# ============================================================

def wait_for_manual_verification(page: Page) -> None:

    print()
    print("=" * 70)
    print("MANUAL VERIFICATION REQUIRED")
    print("=" * 70)

    print()
    print("A SAGA security check may be displayed in Chromium.")
    print()
    print("Please:")
    print("  1. Look at the Chromium window.")
    print("  2. Complete the Friendly Captcha manually.")
    print("  3. Wait until the apartment search page is visible.")
    print()
    print("The script will NOT solve or bypass the CAPTCHA.")
    print()
    print("Waiting for verification...")

    # Poll the page until the obvious verification text
    # disappears or the user has otherwise reached the
    # normal apartment search page.
    #
    # We intentionally give the human plenty of time.
    for _ in range(180):

        page.wait_for_timeout(1_000)

        verification = detect_verification(page)

        if not verification["detected"]:

            print()
            print("[✓] Verification indicators disappeared.")
            print("[→] Continuing reconnaissance...")
            return

    print()
    print("[!] Verification was not detected as completed.")
    print("[→] Continuing anyway so we can inspect the page.")


# ============================================================
# Main
# ============================================================

def main() -> None:

    ensure_directories()

    print()
    print("=" * 70)
    print("SAGA APARTMENT SEARCH - RECONNAISSANCE")
    print("=" * 70)

    print()
    print("Target URL:")
    print(f"  {SAGA_URL}")

    network_requests = []
    network_responses = []

    with sync_playwright() as playwright:

        print()
        print("[→] Starting Chromium...")

        browser = playwright.chromium.launch(
            headless=False,
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 1000,
            },
        )

        page = context.new_page()

        # ----------------------------------------------------
        # Network listeners
        # ----------------------------------------------------

        def on_request(request: Request) -> None:
            try:
                network_requests.append(
                    request_info(request)
                )
            except Exception:
                pass

        def on_response(response: Response) -> None:
            try:
                network_responses.append(
                    response_info(response)
                )
            except Exception:
                pass

        page.on(
            "request",
            on_request,
        )

        page.on(
            "response",
            on_response,
        )

        # ----------------------------------------------------
        # Open SAGA
        # ----------------------------------------------------

        print()
        print("[→] Opening SAGA apartment search...")

        try:

            response = page.goto(
                SAGA_URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            if response:
                print(
                    f"[→] Initial response: "
                    f"HTTP {response.status}"
                )

        except Exception as exc:

            print()
            print(f"[!] Navigation error: {exc}")

        # ----------------------------------------------------
        # Give page JavaScript time to initialize
        # ----------------------------------------------------

        print()
        print("[→] Waiting for initial page initialization...")

        page.wait_for_timeout(5_000)

        # ----------------------------------------------------
        # Detect CAPTCHA
        # ----------------------------------------------------

        verification = detect_verification(page)

        if verification["detected"]:

            print()
            print("[!] Security verification detected.")

            for indicator in verification["indicators"]:
                print(f"    - {indicator}")

            wait_for_manual_verification(page)

        else:

            print()
            print(
                "[✓] No obvious verification challenge detected."
            )

        # ----------------------------------------------------
        # Allow post-verification requests
        # ----------------------------------------------------

        print()
        print(
            "[→] Waiting 10 seconds for listings/network "
            "requests to finish..."
        )

        page.wait_for_timeout(10_000)

        # ----------------------------------------------------
        # Inspect page
        # ----------------------------------------------------

        print()
        print("[→] Inspecting final page...")

        page_data = inspect_page(page)

        print()
        print("[✓] Title:")
        print(f"    {page_data['title']}")

        print()
        print("[✓] Final URL:")
        print(f"    {page_data['url']}")

        # ----------------------------------------------------
        # Listing candidates
        # ----------------------------------------------------

        candidates = find_listing_candidates(page)

        print()
        print(
            f"[✓] Listing candidate links: "
            f"{len(candidates)}"
        )

        for candidate in candidates[:50]:

            print()
            print(
                f"    Text: "
                f"{candidate.get('text', '')[:150]}"
            )

            print(
                f"    URL:  "
                f"{candidate.get('href', '')}"
            )

        # ----------------------------------------------------
        # Network summary
        # ----------------------------------------------------

        print()
        print("[→] Network summary:")

        print(
            f"    Requests:  {len(network_requests)}"
        )

        print(
            f"    Responses: {len(network_responses)}"
        )

        print()
        print("[→] Potential API/network requests:")

        interesting_types = {
            "xhr",
            "fetch",
        }

        interesting_responses = [
            response
            for response in network_responses
            if response["resource_type"]
            in interesting_types
        ]

        for response in interesting_responses:

            print(
                f"    HTTP {response['status']} "
                f"{response['resource_type']:5} "
                f"{response['url']}"
            )

        # ----------------------------------------------------
        # Save artifacts
        # ----------------------------------------------------

        print()
        print("[→] Saving post-verification artifacts...")

        page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=True,
        )

        HTML_PATH.write_text(
            page.content(),
            encoding="utf-8",
        )

        save_json(
            NETWORK_PATH,
            {
                "captured_at": timestamp(),
                "requests": network_requests,
                "responses": network_responses,
            },
        )

        final_verification = detect_verification(page)

        summary = {
            "captured_at": timestamp(),
            "target_url": SAGA_URL,
            "final_url": page.url,
            "title": page_data["title"],
            "verification": final_verification,
            "listing_candidates": candidates,
            "network": {
                "request_count": len(network_requests),
                "response_count": len(network_responses),
                "xhr_fetch_count": len(
                    interesting_responses
                ),
            },
        }

        save_json(
            SUMMARY_PATH,
            summary,
        )

        # ----------------------------------------------------
        # Finish
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("RECONNAISSANCE FINISHED")
        print("=" * 70)

        print()
        print("Artifacts:")

        print(f"  Screenshot:")
        print(f"    {SCREENSHOT_PATH}")

        print(f"  HTML:")
        print(f"    {HTML_PATH}")

        print(f"  Network:")
        print(f"    {NETWORK_PATH}")

        print(f"  Summary:")
        print(f"    {SUMMARY_PATH}")

        print()
        print("[→] Closing Chromium...")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()