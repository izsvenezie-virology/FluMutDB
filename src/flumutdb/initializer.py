from pathlib import Path

from peewee import SqliteDatabase

from flumutdb.models import DbVersion, database_proxy

_BUNDLED_DB = Path(__file__).parent / "data" / "flumut_db.sqlite"


def initialize(db_path=None, read_only=True):
    """Connect to the FluMutDB database.

    Args:
        db_path: Path to a SQLite database file. Uses the bundled database if
                 not provided.
        read_only: Whether to open the database in read-only mode.

    Raises:
        FileNotFoundError: If the given path does not exist.
    """
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
    DbVersion.check_compatibility()
