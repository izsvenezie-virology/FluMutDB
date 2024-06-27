import sqlite3
from urllib.request import urlretrieve
from importlib_resources import files

_DB_FILE = files('flumut_db_data').joinpath('flumut_db.sqlite')

def get_db_file() -> str:
    return _DB_FILE

def update_db_file():
    url = 'https://github.com/izsvenezie-virology/FluMutDB/releases/latest/download/FluMutDB.sqlite3'
    _ = urlretrieve(url, _DB_FILE)

def get_db_version():
    connection = sqlite3.connect(_DB_FILE)
    cursor = connection.cursor()
    major, minor, date = cursor.execute('SELECT * FROM db_version').fetchone()
    connection.close()
    return major, minor, date
