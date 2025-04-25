from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from starlette import status

from src.auth.service import AuthService, get_auth_service
from src.database import get_db
from src.schemas import UserForm

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
        user: UserForm,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db)
):
    data = auth_service.register(user, db)
    response.set_cookie("access_token", data, 3600)
    return {
        "data" : {
            "token": data
        }
    }


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(
        user: UserForm,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db)
):
    data = auth_service.login(user, db)
    response.set_cookie("access_token", data)
    return {
        "data" : {
            "token": data
        }
    }