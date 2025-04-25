from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from src.auth.service import get_current_auth_user_info
from src.crud import get_session_by_id, get_seats_for_session, get_filtered_sessions, get_movie_by_id, \
    get_hall_by_id
from src.database import get_db
from src.schemas import SessionFilters, UserInfo

router = APIRouter(
    tags=["sessions"],
    prefix="/sessions"
)

@router.get(
    "",
    description="Получает все сеансы в кинотеатре",
    summary="Список сеансов в кинотеатре",
)
def get_all_sessions(
        db: Session = Depends(get_db),
        filters: SessionFilters = Query(),
        user: UserInfo = Depends(get_current_auth_user_info)
):
    sessions = get_filtered_sessions(filters, db)

    return {
        "data": [
            {
                "id": session.id,
                "movie": {
                    "id": session.movie.id,
                    "title": session.movie.title,
                    "director": session.movie.director,
                    "screenwriter": session.movie.screenwriter,
                    "actors": session.movie.actors,
                    "description": session.movie.description,
                    "trailerUrl": session.movie.trailer_url,
                    "posterUrl": session.movie.poster_url,
                    "ageRating": session.movie.age_rating,
                    "duration": session.movie.duration
                },
                "hall": session.hall,
                "startTime": session.start_time
            }
            for session in sessions
        ]
    }

@router.get(
    "/{id}",
    description="Получает подробную информацию о фильме текущего сеанса",
    summary="Подробная информация о сеансе",
)
def get_session(
        id: int,
        db: Session = Depends(get_db),
        user: UserInfo = Depends(get_current_auth_user_info)
):
    session = get_session_by_id(id, db)
    movie = get_movie_by_id(session.movie_id, db)
    return {
        "data" : {
            "id": session.id,
            "movie": {
                "id": movie.id,
                "title": movie.title,
                "director": movie.director,
                "screenwriter": movie.screenwriter,
                "genres": movie.genres,
                "actors": movie.actors,
                "description": movie.description,
                "trailerUrl": movie.trailer_url,
                "posterUrl": movie.poster_url,
                "ageRating": movie.age_rating,
                "duration": movie.duration,
            },
            "hall": get_hall_by_id(session.hall_id, db),
            "startTime": session.start_time
        }
    }

@router.get(
    "/{id}/seats",
    description="Получает список всех места в зале для текущего сеанса",
    summary="Список мест для сеанса",
    status_code=status.HTTP_200_OK
)
def seats_for_session(
        id: int,
        db: Session = Depends(get_db),
        user: UserInfo = Depends(get_current_auth_user_info)
):
    seats = get_seats_for_session(id, db)

    return {
        "data" : [
            {
                "id": seat.id,
                "hallId": seat.hall_id,
                "rowNumber": seat.row_number,
                "seatNumber": seat.seat_number,
                "price": seat.price,
                "isAvailable": seat.is_available
            }
            for seat in seats
        ]
    }

