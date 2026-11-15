"""create search events table

Revision ID: ea5d1ce290d4
Revises: 454ac8fb2d41
Create Date: 2026-11-15 22:39:30.036325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea5d1ce290d4'
down_revision = '454ac8fb2d41'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "search_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sa.String(),
            server_default=sa.text("'All'"),
            nullable=False,
        ),
        sa.Column(
            "emotion",
            sa.String(),
            server_default=sa.text("'All'"),
            nullable=False,
        ),
        sa.Column(
            "searched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )


def downgrade():
    op.drop_table("search_events", schema="public")
