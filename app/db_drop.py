import db


def main():
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute('drop table if exists users cascade;')


if __name__ == '__main__':
    main()
