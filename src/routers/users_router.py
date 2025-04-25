from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from src.auth.service import get_current_auth_user_info, is_admin
from src.crud import get_all_users, get_user_orders
from src.database import get_db
from src.schemas import User

router = APIRouter(
    tags=["users"],
    prefix="/users"
)

@router.get(
    "",
    description="Получает список данных о пользователях",
    summary="Список пользователей"
)
def get_users(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_auth_user_info)
):
    is_admin(user)

    users = get_all_users(db)

    return {
        "data" : [
            {
                "id" : user.id,
                "email" : user.email,
                "isAdmin" : user.is_admin,
                "createdAt" : user.created_at
            }
            for user in users
        ]
    }

@router.get(
    "/{id}/orders",
    description="Получает данные о заказах конкретного пользователя",
    summary="Список заказов пользователя"
)
def get_user_all_orders(
        id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_auth_user_info)
):
    is_admin(user)

    orders = get_user_orders(id, db)
    return {
        "data" : [
            {
                "id" : order.id,
                "userId" : order.user_id,
                "sessionId" : order.session_id,
                "totalPrice" : order.total_price,
                "info" : order.info,
                "createdAt" : order.created_at,
                "seats" : [
                    {
                        "id" : seat.id,
                        "hallId" : seat.hall_id,
                        "rowNumber" : seat.row_number,
                        "seatNumber" : seat.seat_number,
                        "price" : seat.price,
                    }
                    for seat in order.seats
                ]
            }
            for order in orders
        ]
    }