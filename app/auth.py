from hashlib import scrypt
from secrets import token_bytes

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
