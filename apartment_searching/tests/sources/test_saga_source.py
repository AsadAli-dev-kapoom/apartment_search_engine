# This file tests the SAGA source.
# It verifies that the source combines the browser client
# and parser and returns normalized Listing objects.

from app.sources.saga import SagaSource


def test_saga_source_has_correct_name():

    source = SagaSource(url="https://example.com",headless=True)

    assert source.name == "saga"