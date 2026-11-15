from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class SearchEvent(db.Model):
    __tablename__ = "search_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="All",
        server_default=text("'All'"),
    )
    emotion: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="All",
        server_default=text("'All'"),
    )
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
