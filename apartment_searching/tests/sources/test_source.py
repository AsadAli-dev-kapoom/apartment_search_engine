# This file tests the SAGA source lifecycle.
# It verifies that the browser session is started once
# and reused across multiple listing checks.

from unittest.mock import Mock

from app.sources.saga.source import SagaSource


def test_source_reuses_browser_session():

    source = SagaSource(
        url="https://example.com",
        headless=True,
    )

    source.client = Mock()
    source.parser = Mock()

    source.parser.parse.side_effect = [
        ["listing-1"],
        ["listing-1", "listing-2"],
    ]

    source.start()
    source.fetch_listings()
    source.fetch_listings()

    source.client.start.assert_called_once()
    source.client.wait_for_listings.assert_called_once()

    assert source.parser.parse.call_count == 2

    source.close()

    source.client.close.assert_called_once()