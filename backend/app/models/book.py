from sqlalchemy import BigInteger, Enum as SQLAlchemyEnum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .enums import BookCategory
from ..extensions import db


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    isbn13: Mapped[str | None] = mapped_column(String)
    isbn10: Mapped[str | None] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, nullable=False)
    authors: Mapped[str | None] = mapped_column(Text)
    categories: Mapped[str | None] = mapped_column(Text)
    thumbnail: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    published_year: Mapped[int | None] = mapped_column(Integer)
    average_rating: Mapped[float | None] = mapped_column(Float)
    num_pages: Mapped[int | None] = mapped_column(Integer)
    ratings_count: Mapped[int | None] = mapped_column(Integer)
    title_and_subtitle: Mapped[str | None] = mapped_column(Text)
    tagged_description: Mapped[str | None] = mapped_column(Text)
    simple_categories: Mapped[BookCategory | None] = mapped_column(
        SQLAlchemyEnum(
            BookCategory,
            name="bookcategory",
            native_enum=True,
            values_callable=lambda enum_cls: [category.value for category in enum_cls],
            schema="public",
        ),
        nullable=True,
    )
    anger: Mapped[float | None] = mapped_column(Float)
    disgust: Mapped[float | None] = mapped_column(Float)
    fear: Mapped[float | None] = mapped_column(Float)
    joy: Mapped[float | None] = mapped_column(Float)
    sadness: Mapped[float | None] = mapped_column(Float)
    surprise: Mapped[float | None] = mapped_column(Float)
    neutral: Mapped[float | None] = mapped_column(Float)
