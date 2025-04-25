from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.service import get_current_auth_user_info
from src.crud import add_order
from src.database import get_db
from src.schemas import OrderCreate, UserInfo

router = APIRouter(
    tags=["orders"],
    prefix="/orders"
)


@router.post(
    "",
    description="Создает заказ и бронирует места в зале",
    summary="Создать заказ"
)
def create_order(
        order: OrderCreate,
        db: Session = Depends(get_db),
        user: UserInfo = Depends(get_current_auth_user_info)
):
    order = add_order(order, db)

    return {
        "data" : {
            "id" : order.id,
            "userId": order.user_id,
            "sessionId": order.session_id,
            "totalPrice": order.total_price,
            "info": order.info,
            "createdAt": order.created_at
        }
    }


