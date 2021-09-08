"""add_schedule_info

Revision ID: b2a5d1bb62da
Revises: c28d2df0e6ca
Create Date: 2021-08-04 11:00:40.306707

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b2a5d1bb62da"
down_revision = "c28d2df0e6ca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "ligne_de_commande", sa.Column("schedule_priority", sa.Integer(), nullable=True)
    )
    op.execute("UPDATE ligne_de_commande SET schedule_priority = 1")
    op.alter_column(
        "ligne_de_commande", "schedule_priority", type_=sa.Integer(), nullable=False
    )

    op.add_column(
        "ligne_de_commande", sa.Column("scheduled_at", sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("ligne_de_commande", "scheduled_at")
    op.drop_column("ligne_de_commande", "schedule_priority")
    # ### end Alembic commands ###