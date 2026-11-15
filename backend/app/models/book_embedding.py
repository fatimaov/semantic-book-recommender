from pgvector.sqlalchemy import VECTOR
from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class BookEmbedding(db.Model):
    __tablename__ = "book_embeddings"
    __table_args__ = (
        UniqueConstraint("book_id", "model", name="uq_book_embeddings_book_id_model"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(String, nullable=False)
    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=768,
        server_default=text("768"),
    )
    embedding: Mapped[list[float]] = mapped_column(VECTOR(768), nullable=False)

    book: Mapped["Book"] = relationship(back_populates="embeddings")
