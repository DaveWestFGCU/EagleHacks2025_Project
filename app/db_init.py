"""Initialize the database.

This module is intended only for standalone usage so that you can create
and populate the database before running the backend.

To refresh the database following an update to 'db_init.py', drop the
database's contents using 'db_drop.py' before re-running 'db_init.py'.

You can only create a database by connecting to an existing
database, and similarly, you can only create a user by connecting
as an existing user. To work around that, we assume that we can
connect to the 'postgres' database as the 'postgres' user. You
must supply the password via the 'PGPASSWORD' environment variable.
The 'PGPASSWORD' environment variable and more are documented in
<https://www.postgresql.org/docs/current/libpq-envars.html>.
"""

import contextlib

from psycopg.errors import DuplicateDatabase, DuplicateObject
from psycopg.sql import SQL, Identifier, Literal

import db


def main():
    # Don't worry if the user already exists.
    with contextlib.suppress(DuplicateObject):
        _create_user()

    # Similarly, don't worry if the database already exists.
    with contextlib.suppress(DuplicateDatabase):
        _create_db()

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("""
            create table if not exists users (
                user_id bigserial primary key,
                username varchar(256) not null unique check (username <> ''),
                pw_hash bytea not null,
                salt bytea not null,
                api_key text not null unique
            );
        """)


def _connect_as_superuser(name: str | None = 'postgres'):
    # Let the password be manually specified through 'PGPASSWORD'.
    return db.connect(name=name, user='postgres', password=None)


def _create_db():
    with _connect_as_superuser() as conn, conn.cursor() as cursor:
        cursor.execute(
            SQL('create database {} owner {};').format(
                Identifier(db.DB_NAME), Identifier(db.DB_USER)
            )
        )


def _create_user():
    with _connect_as_superuser() as conn, conn.cursor() as cursor:
        cursor.execute(
            SQL('create user {} password {};').format(
                Identifier(db.DB_USER), Literal(db.DB_PASSWORD)
            )
        )


if __name__ == '__main__':
    main()
