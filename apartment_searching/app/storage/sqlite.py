# This file implements listing storage using SQLite.
# It persists normalized listings so the monitoring system
# can detect listings that have appeared since the previous check.

import sqlite3
from datetime import datetime

from datetime import timezone

from app.models import Listing
from app.storage.base import ListingRepository


class SQLiteListingRepository(ListingRepository):
    """SQLite implementation of the listing repository."""

    def __init__(self, database_path: str):
        self.database_path = database_path
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        """Create a database connection."""

        return sqlite3.connect(self.database_path)

    def _initialize_database(self) -> None:
        """Create the listings table if it does not exist."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS listings (
                    source TEXT NOT NULL,
                    listing_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    first_seen_at TEXT,
                    last_seen_at TEXT,
                    PRIMARY KEY (source, listing_id)
                )
                """
            )

    def save(self, listing: Listing) -> None:
        """Store a listing or update its last-seen timestamp."""

        now = datetime.now(timezone.utc)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO listings (
                    source,
                    listing_id,
                    url,
                    first_seen_at,
                    last_seen_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source, listing_id)
                DO UPDATE SET
                    url = excluded.url,
                    last_seen_at = excluded.last_seen_at
                """,
                (
                    listing.source,
                    listing.listing_id,
                    listing.url,
                    self._serialize_datetime(now),
                    self._serialize_datetime(now),
                ),
            )


    def get(self, source: str, listing_id: str) -> Listing | None:
        """Return a stored listing by source and ID."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    source,
                    listing_id,
                    url,
                    first_seen_at,
                    last_seen_at
                FROM listings
                WHERE source = ? AND listing_id = ?
                """,
                (source, listing_id),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_listing(row)

    def get_all(self) -> list[Listing]:
        """Return all stored listings."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    source,
                    listing_id,
                    url,
                    first_seen_at,
                    last_seen_at
                FROM listings
                """
            ).fetchall()

        return [self._row_to_listing(row) for row in rows]

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        """Convert a datetime to a SQLite-compatible string."""

        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _deserialize_datetime(value: str | None) -> datetime | None:
        """Convert a SQLite string back to a datetime."""

        if value is None:
            return None

        return datetime.fromisoformat(value)

    def _row_to_listing(self, row) -> Listing:
        """Convert a database row into a Listing."""

        return Listing(
            source=row[0],
            listing_id=row[1],
            url=row[2],
            first_seen_at=self._deserialize_datetime(row[3]),
            last_seen_at=self._deserialize_datetime(row[4]),
        )