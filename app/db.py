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
    return Connection[NamedTuple].connect(
        autocommit=True,
        row_factory=namedtuple_row,
        host='localhost',
        dbname=name,
        user=user,
        password=password,
        client_encoding='UTF8',
    )
