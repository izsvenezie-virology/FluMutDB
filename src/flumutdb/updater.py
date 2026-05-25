import os
import tempfile
from pathlib import Path
from urllib.request import urlretrieve

from flumutdb.core import BUNDLED_DB, USER_DB
from flumutdb.initializer import initialize

_DOWNLOAD_URL = (
    "https://github.com/izsvenezie-virology/FluMutDB"
    "/releases/latest/download/flumut_db.sqlite"
)


def update() -> None:
    """Download the latest FluMutDB database and re-initialize the connection.

    Updates the bundled database in-place when it is writable (development
    installs, user-owned environments). Falls back to the environment-scoped
    user directory when the bundled location is not writable (system installs).

    Raises:
        urllib.error.URLError: If the download fails.
        PermissionError: If neither destination is writable.
    """
    if os.access(BUNDLED_DB, os.W_OK):
        dest = BUNDLED_DB
    else:
        USER_DB.parent.mkdir(parents=True, exist_ok=True)
        dest = USER_DB
    _atomic_download(dest)
    initialize()


def _atomic_download(dest: Path) -> None:
    """Download the database to dest using a sibling temp file for atomicity.

    On failure the temp file is removed and dest is left untouched.
    """
    tmp_fd, tmp_path = tempfile.mkstemp(dir=dest.parent, suffix=".tmp")
    try:
        os.close(tmp_fd)
        urlretrieve(_DOWNLOAD_URL, tmp_path)
        os.replace(tmp_path, dest)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
