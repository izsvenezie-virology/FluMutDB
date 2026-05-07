from pathlib import Path

from peewee import DatabaseProxy

REQUIRED_MAJOR_VERSION = 7

DATABASE_PROXY = DatabaseProxy()
BUNDLED_DB = Path(__file__).parent / "data" / "flumut_db.sqlite"
