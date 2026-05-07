from pathlib import Path
from typing import Optional

from peewee import SqliteDatabase

from flumutdb.core import BUNDLED_DB, DATABASE_PROXY
from flumutdb.models import DbVersion, Marker, Segment


def initialize(
    db_path: Optional[str] = None,
    read_only: bool = True,
):
    """Connect to the FluMutDB database.

    Args:
        db_path: Path to a SQLite database file. Uses the bundled database if
                 not provided.
        read_only: Whether to open the database in read-only mode.

    Raises:
        FileNotFoundError: If the given path does not exist.
    """
    path = Path(db_path) if db_path is not None else BUNDLED_DB
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    if read_only:
        db = SqliteDatabase(
            f"file:{path}?mode=ro", uri=True, pragmas={"foreign_keys": 1}
        )
    else:
        db = SqliteDatabase(path, pragmas={"foreign_keys": 1})
    DATABASE_PROXY.initialize(db)
    DbVersion.is_compatible()
    Segment.clear_cache()
    Marker.clear_cache()
