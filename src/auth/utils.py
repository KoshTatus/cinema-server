from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.jwt_auth.utils import hash_password
from src.models import UsersOrm
from src.schemas import UserCreate

from src.schemas import User


def user_exist(email: str, db: Session):
    res = db.execute(select(UsersOrm).where(UsersOrm.email == email)).first()
    if res:
        return True
    return False

def get_users(db: Session):
    return [User.model_validate(row, from_attributes=True) for row in db.execute(select(UsersOrm)).scalars().all()]

def add_user(user: UserCreate, db: Session):
    new_user = UsersOrm(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

def email_exist(email: str, db: Session):
    return True if db.execute(select(UsersOrm.email).where(UsersOrm.email == email)).scalars().first() else False

def password_exist(password: str, db: Session):
    password_hash = hash_password(password)
    return True if db.execute(select(UsersOrm.password_hash).where(UsersOrm.password_hash == password_hash)).scalars().first() else False