__version__ = "7.0.0"
__author__ = "Edoardo Giussani"
__contact__ = "egiussani@izsvenezie.it"

from pathlib import Path

from peewee import SqliteDatabase

from .loader import _clear_cache, load_segments
from .models import (
    Annotation,
    DbVersion,
    Effect,
    Marker,
    MarkerEffect,
    MarkerMutation,
    Mutation,
    MutationMapping,
    Paper,
    Protein,
    Reference,
    Segment,
    database_proxy,
)

__all__ = [
    "init",
    "load_segments",
    "Annotation",
    "DbVersion",
    "Effect",
    "Marker",
    "MarkerEffect",
    "MarkerMutation",
    "Mutation",
    "MutationMapping",
    "Paper",
    "Protein",
    "Reference",
    "Segment",
]

_BUNDLED_DB = Path(__file__).parent / "data" / "flumut_db.sqlite"


def init(db_path=None, read_only=True):
    """Connect to the FluMutDB database.

    Args:
        db_path: Path to a SQLite database file. Uses the bundled database if
                 not provided.
        read_only: Whether to open the database in read-only mode.

    Raises:
        FileNotFoundError: If the given path does not exist.
    """
    _clear_cache()
    path = Path(db_path) if db_path is not None else _BUNDLED_DB
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    if read_only:
        db = SqliteDatabase(
            f"file:{path}?mode=ro", uri=True, pragmas={"foreign_keys": 1}
        )
    else:
        db = SqliteDatabase(path, pragmas={"foreign_keys": 1})
    database_proxy.initialize(db)
