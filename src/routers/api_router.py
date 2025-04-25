from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.auth_router import router as auth_router
from src.auth.service import get_current_auth_user_info
from src.crud import get_all_genres, delete_user_order
from src.database import get_db
from src.routers.orders_router import router as orders_router
from src.routers.session_router import router as session_router
from src.routers.users_router import router as users_router
from src.schemas import UserInfo

router = APIRouter(
    prefix="/api",
)

router.include_router(session_router)
router.include_router(orders_router)
router.include_router(auth_router)
router.include_router(users_router)


@router.get(
    "/genres",
    description="Получает всю информацию о жанрах",
    summary="Получить список жанров",
    tags=["utils"]
)
def get_genres_all(
        db: Session = Depends(get_db),
        user: UserInfo = Depends(get_current_auth_user_info)
):
    genres = get_all_genres(db)

    return {
        "data" : [
            {
                "id" : genre.id,
                "name" : genre.name
            }
            for genre in genres
        ]
    }

@router.delete(
    "/orders/{id}",
    description="Удалить заказ и бронь мест пользователя",
    summary="Удалить заказ",
    tags=["utils"]
)
def delete_order(
        id: int,
        db: Session = Depends(get_db)
):
    delete_user_order(id, db)

    return {
        "data" : {
            "msg" : "Order deleted"
        }
    }