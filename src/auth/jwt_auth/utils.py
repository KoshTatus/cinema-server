import hashlib

from jwt.exceptions import InvalidTokenError
from src.auth.errors import AuthErrors
from src.auth.jwt_auth.base.auth import JWTAuth


def try_to_decode_token(jwt_auth: JWTAuth, token: str) -> dict | InvalidTokenError:
    try:
        payload = jwt_auth.verify_token(token)
        return payload
    except InvalidTokenError:
        raise AuthErrors.invalid_token()

def hash_password(password: str):
    coder = hashlib.new("sha256")
    coder.update(password.encode(encoding="utf-8"))
    return coder.hexdigest()