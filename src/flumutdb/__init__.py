import flumutdb
from typing import Tuple

def get_db_file()-> str:
    """Returns path to the DB file.
    
    Returns:
    db_file: `str`
        Path to db file.
    """
    return flumutdb.get_db_file()

def update_db_file()-> None:
    """Update DB file from latest GitHub release.
    """
    return flumutdb.update_db_file()

def get_db_version()-> Tuple[str, str, str]:
    """Display DB version.

    Returns:
    versions: `Tuple[str, str, str]`
        A tuple of major, minor and date.
    """
    return flumutdb.get_db_version()
