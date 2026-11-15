"""create books table

Revision ID: 7b4fcb3242ed
Revises:
Create Date: 2026-11-15 21:54:31.547195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b4fcb3242ed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    book_category = sa.Enum(
        "Fiction",
        "Nonfiction",
        "Children's Fiction",
        "Children's Nonfiction",
        name="bookcategory",
        schema="public",
    )
    book_category.create(op.get_bind())

    op.create_table(
        "books",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("isbn13", sa.String(), nullable=True),
        sa.Column("isbn10", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.Text(), nullable=True),
        sa.Column("categories", sa.Text(), nullable=True),
        sa.Column("thumbnail", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("average_rating", sa.Float(), nullable=True),
        sa.Column("num_pages", sa.Integer(), nullable=True),
        sa.Column("ratings_count", sa.Integer(), nullable=True),
        sa.Column("title_and_subtitle", sa.Text(), nullable=True),
        sa.Column("tagged_description", sa.Text(), nullable=True),
        sa.Column("simple_categories", book_category, nullable=True),
        sa.Column("anger", sa.Float(), nullable=True),
        sa.Column("disgust", sa.Float(), nullable=True),
        sa.Column("fear", sa.Float(), nullable=True),
        sa.Column("joy", sa.Float(), nullable=True),
        sa.Column("sadness", sa.Float(), nullable=True),
        sa.Column("surprise", sa.Float(), nullable=True),
        sa.Column("neutral", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )


def downgrade():
    op.drop_table("books", schema="public")
    sa.Enum(
        "Fiction",
        "Nonfiction",
        "Children's Fiction",
        "Children's Nonfiction",
        name="bookcategory",
        schema="public",
    ).drop(op.get_bind())
