# This file exposes the common application models.
# It allows other parts of the application to import models
# directly from the app.models package.

from .listing import Listing

__all__ = ["Listing"]