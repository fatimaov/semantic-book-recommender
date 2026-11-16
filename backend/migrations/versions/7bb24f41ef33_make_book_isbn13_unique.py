"""make book isbn13 unique

Revision ID: 7bb24f41ef33
Revises: ea5d1ce290d4
Create Date: 2026-11-16 15:12:00.991857

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7bb24f41ef33'
down_revision = 'ea5d1ce290d4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_books_isbn13",
        "books",
        ["isbn13"],
        schema="public",
    )


def downgrade():
    op.drop_constraint(
        "uq_books_isbn13",
        "books",
        schema="public",
        type_="unique",
    )
