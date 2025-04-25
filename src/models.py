import datetime

from sqlalchemy import ForeignKey, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from src.enums import AgeRating


class Base(DeclarativeBase):
    pass


class MoviesOrm(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    director: Mapped[str]
    screenwriter: Mapped[str]
    actors: Mapped[list[str]] = mapped_column(ARRAY(String))
    description: Mapped[str]
    trailer_url: Mapped[str]
    poster_url: Mapped[str]
    age_rating: Mapped[AgeRating]
    duration: Mapped[int]

class GenresOrm(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class MovieGenresOrm(Base):
    __tablename__ = "m2m_movies_genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))

class HallsOrm(Base):
    __tablename__ = "halls"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    total_seats: Mapped[int]

class SeatsOrm(Base):
    __tablename__ = "seats"
    id: Mapped[int] = mapped_column(primary_key=True)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id"))
    row_number: Mapped[int]
    seat_number: Mapped[int]
    price: Mapped[int]

class SessionsOrm(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id"))
    start_time: Mapped[datetime.datetime]

class OrdersOrm(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    total_price: Mapped[int]
    info: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())

class UsersOrm(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    email: Mapped[str]
    password_hash: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())

class SeatsOrdersOrm(Base):
    __tablename__ = "m2m_orders_seats"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"))
