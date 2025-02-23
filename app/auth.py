from hashlib import scrypt
from secrets import token_bytes, token_urlsafe

import db

# Sample parameters for interactive login taken from:
# https://cryptobook.nakov.com/mac-and-key-derivation/scrypt#scrypt-parameters
_COST_FACTOR = 16384
_BLOCK_SIZE = 8
_PARALLELISM = 1


def generate_salt() -> bytes:
    return token_bytes(16)


def hash_pw(*, pw: str, salt: bytes) -> bytes:
    return scrypt(pw.encode(), salt=salt, n=_COST_FACTOR, r=_BLOCK_SIZE, p=_PARALLELISM)


def pw_matches_hash(*, pw: str, salt: bytes, hash: bytes) -> bool:
    return hash_pw(pw=pw, salt=salt) == hash


def generate_api_key() -> str:
    return token_urlsafe(16)


def lookup_user_id_from_api_key(api_key: str) -> int | None:
    with db.connect() as conn, conn.cursor() as cursor:
        record = cursor.execute(
            """
            select user_id
            from users
            where api_key = %s;
            """,
            (api_key,),
        ).fetchone()
        if not record:
            return None
        user_id = record.user_id
        assert isinstance(user_id, int)
        return user_id


class UnknownUserError(Exception):
    user_id: int

    def __init__(self, user_id: int):
        super().__init__(f"Unknown user ID '{user_id}'")
        self.user_id = user_id


def get_user_api_key(user_id: int) -> str:
    with db.connect() as conn, conn.cursor() as cursor:
        record = cursor.execute(
            """
            select api_key
            from users
            where user_id = %s;
            """,
            (user_id,),
        ).fetchone()
        if not record:
            raise UnknownUserError(user_id)
        api_key = record.api_key
        assert isinstance(api_key, str)
        return api_key
