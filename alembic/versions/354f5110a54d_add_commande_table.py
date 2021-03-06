"""add commande table

Revision ID: 354f5110a54d
Revises: 98f4927abc23
Create Date: 2018-10-23 19:54:44.018181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '354f5110a54d'
down_revision = '98f4927abc23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('commande',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exact_order_id', sa.String(length=255), nullable=True),
    sa.Column('exact_tier_id', sa.String(length=255), nullable=True),
    sa.Column('exact_order_description', sa.String(length=255), nullable=True),
    sa.Column('exact_your_ref', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['exact_tier_id'], ['tier.exact_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('exact_order_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('commande')
    # ### end Alembic commands ###
