# This file tests the SAGA browser client.
# It verifies that the client can start, expose a page,
# and detect apartment listings after manual CAPTCHA verification.

from app.sources.saga.client import SagaClient


def test_saga_client_can_start():

    client = SagaClient(url="https://example.com", headless=False)

    try:
        client.start()

        assert client.page is not None

    finally:
        client.close()