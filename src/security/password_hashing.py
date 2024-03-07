import bcrypt


def get_password_hash_and_salt(password: str) -> tuple[bytes, bytes]:
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return password_hash, salt


def check_password(password: str, salt: bytes, password_hash: bytes) -> bool:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return password_hash == hashed_password
