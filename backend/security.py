import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("ascii")
def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        return False

    hash_bytes = password_hash.encode("ascii")
    return bcrypt.checkpw(password_bytes, hash_bytes)
def create_access_token(user_id: int) -> str:
    secret = os.environ["JWT_SECRET"]
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, secret, algorithm="HS256")
def read_access_token(token: str) -> int:
    secret = os.environ["JWT_SECRET"]
    payload = jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"require": ["sub", "exp"]},
    )
    return int(payload["sub"])