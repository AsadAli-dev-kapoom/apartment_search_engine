# This file exposes application configuration.
# It provides a simple import point for loading runtime settings.

from .settings import Settings, load_settings

__all__ = ["Settings", "load_settings"]