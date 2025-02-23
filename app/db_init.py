import contextlib

from psycopg.errors import DuplicateDatabase, DuplicateObject
from psycopg.sql import SQL, Identifier, Literal

import db


def main():
    with contextlib.suppress(DuplicateObject):
        _create_user()

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
