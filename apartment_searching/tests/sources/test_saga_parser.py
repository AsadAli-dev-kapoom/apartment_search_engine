# This file tests the SAGA parser.
# It verifies that apartment IDs and URLs are correctly
# extracted from SAGA apartment cards.

from playwright.sync_api import sync_playwright

from app.sources.saga.parser import SagaParser


def test_saga_parser_extracts_listing():

    html = """
    <div id="APARTMENT-card-1">
        <h3>
            <a href="/immo-detail/6783/test-apartment">
                Test Apartment
            </a>
        </h3>
    </div>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_content(html)

        parser = SagaParser()
        listings = parser.parse(page)

        browser.close()

    assert len(listings) == 1

    listing = listings[0]

    assert listing.source == "saga"
    assert listing.listing_id == "6783"
    assert listing.url == (
        "https://www.saga.hamburg/immo-detail/6783/test-apartment"
    )