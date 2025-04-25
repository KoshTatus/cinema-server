from sqlalchemy.orm import Session
from starlette import status

from src.auth.errors import AuthErrors
from fastapi import Request, Depends, HTTPException
from src.auth.jwt_auth.base.auth import JWTAuth
from src.auth.jwt_auth.base.config import JWTConfig
from src.auth.jwt_auth.utils import hash_password, try_to_decode_token
from src.auth.utils import user_exist, add_user, email_exist, password_exist
from src.crud import get_user_by_email
from src.schemas import UserForm, UserCreate, UserInfo, User


class AuthService:
    def __init__(self, jwt_auth: JWTAuth):
        self.jwt_auth = jwt_auth

    def register(self, user: UserForm, db: Session):
        if user_exist(user.email, db):
            raise AuthErrors.email_occupied()
        add_user(
            UserCreate(
                email=user.email,
                password_hash=hash_password(user.password)
            ),
            db
        )

        user = get_user_by_email(user.email, db)

        token = self.jwt_auth.generate_token(
            payload={
                "id" : user.id,
                "isAdmin" : user.is_admin,
            }
        )
        return token

    def login(self, user: UserForm, db: Session):
        if not email_exist(user.email, db):
            raise AuthErrors.email_not_found()
        if not password_exist(user.password, db):
            raise AuthErrors.password_not_found()

        user = get_user_by_email(user.email, db)

        token = self.jwt_auth.generate_token(
            payload={
                "id": user.id,
                "isAdmin": user.is_admin,
            }
        )
        return token

def get_auth_service():
    return AuthService(jwt_auth=JWTAuth(config=JWTConfig()))

def get_current_auth_user_info(
        request: Request,
        auth_service: AuthService = Depends(get_auth_service),
) -> UserInfo | HTTPException:
    cookie_header = request.headers.get("Cookie")
    if not cookie_header:
        return AuthErrors.cookie_not_found()

    token = None
    for chunk in cookie_header.split(";"):
        if "access_token" in chunk:
            token = chunk.split("=")[1].strip()
            break

    if not token:
        return AuthErrors.token_not_found()

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    payload = try_to_decode_token(auth_service.jwt_auth, token)

    return UserInfo(
        id=payload.get("id"),
        is_admin=payload.get("isAdmin"),
    )

def is_admin(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only for a admin")