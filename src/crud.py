from fastapi import HTTPException, status
from sqlalchemy import select, delete, update, func, and_, exists
from sqlalchemy.orm import Session

from src.enums import AgeRating
from src.models import MoviesOrm, GenresOrm, OrdersOrm, SeatsOrm, UsersOrm, MovieGenresOrm, SeatsOrdersOrm, SessionsOrm, \
    HallsOrm
from src.schemas import Movie, Genre, Order, OrderCreate, Hall, Session as SessionSchema, SessionDetailed, Seat, User, \
    UserWithOrders, MovieWithGenres, SeatWithInfo, SessionFilters, OrderDetailed


def fetch_records(model, db: Session, filters=None):
    query = select(model)
    if filters:
        query = query.where(*filters)
    return db.execute(query).scalars().all()

def fetch_by_id(model, id: int, db: Session):
    record = db.execute(select(model).where(model.id == id)).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return record

def delete_record(model, filters, db: Session):
    db.execute(delete(model).where(*filters))
    db.commit()

def update_record(model, filters, values, db: Session):
    query = update(model).where(*filters).values(values)
    db.execute(query)
    db.commit()

def get_all_movies(db: Session) -> list[Movie]:
    movies = fetch_records(MoviesOrm, db)
    return [Movie.model_validate(movie, from_attributes=True) for movie in movies]


def get_genres_to_movie(movie_id: int, db: Session) -> list[Genre]:
    query = (
        select(GenresOrm)
        .join(MovieGenresOrm, GenresOrm.id == MovieGenresOrm.genre_id)
        .filter(MovieGenresOrm.movie_id == movie_id)
    )
    genres = db.execute(query).scalars().all()
    return [Genre.model_validate(genre, from_attributes=True) for genre in genres]


def get_all_orders(
        db: Session
) -> list[Order]:
    query = select(OrdersOrm)
    result = [Order.model_validate(row, from_attributes=True) for row in db.execute(query).all()]

    return result

def add_order(order: OrderCreate, db: Session) -> Order:
    new_order = OrdersOrm(
        user_id=order.user_id,
        session_id=order.session_id,
        total_price=order.total_price,
        info=order.info
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for seat_id in order.seats_ids:
        seat_order = SeatsOrdersOrm(seat_id=seat_id, order_id=new_order.id)
        db.add(seat_order)
        db.commit()
        db.refresh(seat_order)

    return Order.model_validate(new_order, from_attributes=True)


def get_movie_by_id(
        id: int,
        db: Session
) -> MovieWithGenres:
    query = (
        select(
            MoviesOrm.id,
            MoviesOrm.title,
            MoviesOrm.director,
            MoviesOrm.screenwriter,
            func.array_agg(GenresOrm.name).label("genres"),
            MoviesOrm.actors,
            MoviesOrm.description,
            MoviesOrm.trailer_url,
            MoviesOrm.poster_url,
            MoviesOrm.age_rating,
            MoviesOrm.duration,
        )
        .select_from(MoviesOrm)
        .join(MovieGenresOrm, MoviesOrm.id == MovieGenresOrm.movie_id)
        .join(GenresOrm, MovieGenresOrm.genre_id == GenresOrm.id)
        .where(MoviesOrm.id == id)
        .group_by(MoviesOrm.id)
    )
    movie = db.execute(query).first()
    result = MovieWithGenres.model_validate(movie, from_attributes=True)

    return result


def get_hall_by_id(
        id: int,
        db: Session
) -> Hall:
    query = select(HallsOrm).where(HallsOrm.id == id)
    hall = db.execute(query).scalars().first()
    result = Hall.model_validate(hall, from_attributes=True)

    return result


def get_session_by_id(
        id: int,
        db: Session
) -> SessionSchema:
    query = select(SessionsOrm).where(SessionsOrm.id == id)
    session = db.execute(query).scalars().first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    result = SessionSchema.model_validate(session, from_attributes=True)

    return result


def get_all_users(
        db: Session
) -> list[User]:
    query = select(UsersOrm)
    users = db.execute(query).scalars().all()
    result = [
        User.model_validate(user, from_attributes=True)
        for user in users
    ]

    return result

def get_user_by_email(
        email: str,
        db: Session
) -> User:
    query = select(UsersOrm).where(UsersOrm.email == email)
    user = db.execute(query).scalars().first()

    result = User.model_validate(user, from_attributes=True)

    return result


def get_user_orders(
        user_id: int,
        db: Session
) -> list[OrderDetailed]:
    if not db.execute(select(UsersOrm).where(UsersOrm.id == user_id)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = select(OrdersOrm).where(OrdersOrm.user_id == user_id).order_by(OrdersOrm.created_at)
    orders = [
        Order.model_validate(row, from_attributes=True)
        for row in db.execute(query).scalars().all()
    ]

    result = [
        OrderDetailed(
            **order.model_dump(),
            seats=get_seats_for_order(order.id, db)
        ) for order in orders
    ]

    return result


def get_all_users_orders(
        db: Session
) -> list[UserWithOrders]:
    users = [
        User.model_validate(row, from_attributes=True)
        for row in db.execute(select(UsersOrm)).scalars().all()
    ]
    result = [
        UserWithOrders(
            user=user,
            orders=get_user_orders(user.id, db)
        )
        for user in users
    ]

    return result

def get_sessions(
        db: Session
) -> list[SessionSchema]:
    sessions = [
        SessionSchema.model_validate(row, from_attributes=True)
        for row in db.execute(select(SessionsOrm)).scalars().all()
    ]

    return sessions


def get_all_genres(
        db: Session
):
    result = [
        Genre.model_validate(row, from_attributes=True)
        for row in db.execute(select(GenresOrm)).scalars().all()
    ]

    return result

def get_filtered_sessions(filters: SessionFilters, db: Session) -> list[SessionDetailed]:
    query = (
        select(SessionsOrm)
        .distinct(MoviesOrm.id)
        .join(MoviesOrm)
        .join(MovieGenresOrm, MovieGenresOrm.movie_id == MoviesOrm.id)
        .join(GenresOrm, GenresOrm.id == MovieGenresOrm.genre_id)
    )

    filter_conditions = []
    if filters.title:
        filter_conditions.append(MoviesOrm.title.ilike(f"{filters.title}%"))
    if filters.genres:
        genres = filters.genres[0].split(",")
        genre_filters = [GenresOrm.name.ilike(f"%{genre}%") for genre in genres]
        filter_conditions.append(and_(*genre_filters))
    if filters.age_rating:
        age_rating = [value for value in AgeRating if value.value == filters.age_rating]
        if age_rating:
            filter_conditions.append(MoviesOrm.age_rating == age_rating[0])
    filter_conditions.extend([
        filters.start_date <= SessionsOrm.start_time,
        SessionsOrm.start_time <= filters.end_date
    ])

    if filter_conditions:
        query = query.filter(and_(*filter_conditions))

    sessions = db.execute(query).scalars().all()
    return [
        SessionDetailed(
            id=session.id,
            movie=get_movie_by_id(session.movie_id, db),
            hall=get_hall_by_id(session.hall_id, db),
            start_time=session.start_time
        ) for session in sessions
    ]


def get_seats_for_order(order_id: int, db: Session) -> list[Seat]:
    query = (
        select(SeatsOrm)
        .join(SeatsOrdersOrm, SeatsOrdersOrm.seat_id == SeatsOrm.id)
        .filter(SeatsOrdersOrm.order_id == order_id)
    )
    seats = db.execute(query).scalars().all()
    return [Seat.model_validate(seat, from_attributes=True) for seat in seats]

def get_seats_for_session(
        session_id: int,
        db: Session
):
    seat_order_subquery = (
        exists()
        .where(
            and_(
                SeatsOrdersOrm.seat_id == SeatsOrm.id,
                SeatsOrdersOrm.order_id == OrdersOrm.id,
                OrdersOrm.session_id == session_id
            )
        )
    )

    query = (
        select(
            SeatsOrm,
            seat_order_subquery.label("is_available")
        )
        .join(SessionsOrm, SessionsOrm.hall_id == SeatsOrm.hall_id)
        .filter(SessionsOrm.id == session_id)
        .order_by(SeatsOrm.seat_number, SeatsOrm.row_number)
    )

    result = db.execute(query).all()
    seats = []
    for seat, is_available in result:
        seats.append(
            SeatWithInfo(
                id=seat.id,
                hall_id=seat.hall_id,
                row_number=seat.row_number,
                seat_number=seat.seat_number,
                price=seat.price,
                is_available=not is_available
            )
        )

    return seats

def delete_user_order(order_id: int, db: Session):
    delete_record(SeatsOrdersOrm, [SeatsOrdersOrm.order_id == order_id], db)
    delete_record(OrdersOrm, [OrdersOrm.id == order_id], db)
