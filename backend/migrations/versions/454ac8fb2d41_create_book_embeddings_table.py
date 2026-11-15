"""create book embeddings table

Revision ID: 454ac8fb2d41
Revises: 7b4fcb3242ed
Create Date: 2026-11-15 22:33:46.959567

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision = '454ac8fb2d41'
down_revision = '7b4fcb3242ed'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "book_embeddings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("book_id", sa.BigInteger(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column(
            "dimensions",
            sa.Integer(),
            server_default=sa.text("768"),
            nullable=False,
        ),
        sa.Column("embedding", VECTOR(768), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "book_id", "model", name="uq_book_embeddings_book_id_model"
        ),
        schema="public",
    )


def downgrade():
    op.drop_table("book_embeddings", schema="public")
