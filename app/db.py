"""Database helper module

The `DB_*` constants control how the backend connects to the database,
and the `connect` function opens a preconfigured connection.
"""

__all__ = ['DB_NAME', 'DB_PASSWORD', 'DB_USER', 'connect']

from typing import NamedTuple

from psycopg import Connection
from psycopg.rows import namedtuple_row

DB_NAME = 'eaglehacks_2025'
DB_USER = 'eaglehacks_2025'
DB_PASSWORD = 'password'  # FIXME


def connect(
    name: str | None = DB_NAME,
    user: str | None = DB_USER,
    password: str | None = DB_PASSWORD,
) -> Connection[NamedTuple]:
    """Open a connection to the database.

    The connection uses the named tuple row factory so that you can read
    columns by name and by index. Note that autocommit is enabled.
    """
    return Connection[NamedTuple].connect(
        autocommit=True,
        row_factory=namedtuple_row,
        # The backend and database server are on the same computer.
        host='localhost',
        dbname=name,
        user=user,
        password=password,
        client_encoding='UTF8',
    )
