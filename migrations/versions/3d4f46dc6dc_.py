"""empty message

Revision ID: 3d4f46dc6dc
Revises: 411338af42b
Create Date: 2015-01-17 16:53:55.124638

"""

# revision identifiers, used by Alembic.
revision = '3d4f46dc6dc'
down_revision = '411338af42b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipes', sa.Column('bean_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipes', 'bean_id')
    ### end Alembic commands ###
