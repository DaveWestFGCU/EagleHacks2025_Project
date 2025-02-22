import contextlib

from psycopg.errors import DuplicateDatabase, DuplicateObject
from psycopg.sql import SQL, Identifier, Literal

import db


def main():
    with contextlib.suppress(DuplicateDatabase):
        _create_db()

    with contextlib.suppress(DuplicateObject):
        _create_user()

    _make_owner()

    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute("""
            create table if not exists users (
                primary key (user_id),
                unique (username),
                user_id bigserial not null,
                username varchar(256) not null check (username <> ''),
                pw_hash bytea not null,
                salt bytea not null
            );
        """)


def _connect_as_superuser(name: str | None = 'postgres'):
    # Let the password be manually specified through 'PGPASSWORD'.
    return db.connect(name=name, user='postgres', password=None)


def _create_db():
    with _connect_as_superuser() as conn, conn.cursor() as cursor:
        cursor.execute(SQL('create database {};').format(Identifier(db.DB_NAME)))


def _create_user():
    with _connect_as_superuser() as conn, conn.cursor() as cursor:
        cursor.execute(
            SQL('create user {} password {};').format(
                Identifier(db.DB_USER), Literal(db.DB_PASSWORD)
            )
        )


def _make_owner():
    with _connect_as_superuser(name=db.DB_NAME) as conn, conn.cursor() as cursor:
        cursor.execute(
            SQL(
                """
                alter database {name} owner to {user};
                alter schema public owner to {user};
                """
            ).format(
                name=Identifier(db.DB_NAME),
                user=Identifier(db.DB_USER),
            )
        )


if __name__ == '__main__':
    main()
