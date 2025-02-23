"""Drop the primary database's contents.

This module is intended only for standalone usage so that you can reset
the database before re-running 'db_init.py'.
"""

import db


def main():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute('drop table if exists users cascade;')


if __name__ == '__main__':
    main()
