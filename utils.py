# models.py
import sqlite3

from config import DATABASE


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def is_integer(s):
    try:
        int(s)
        if int(s) < 0:
            return False
        return True
    except ValueError:
        return False
