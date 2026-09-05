# This file tests the storage interface.
# It verifies that concrete storage implementations must provide
# the required listing operations.

from app.storage import ListingRepository


def test_listing_repository_is_abstract():

    assert ListingRepository.__abstractmethods__ == {
        "save",
        "get",
        "get_all",
    }