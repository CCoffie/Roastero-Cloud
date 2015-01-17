"""empty message

Revision ID: 3d3867b0656
Revises: 2e755a8f0ed
Create Date: 2015-01-17 15:16:21.805919

"""

# revision identifiers, used by Alembic.
revision = '3d3867b0656'
down_revision = '2e755a8f0ed'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipes', sa.Column('creator_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipes', 'creator_id')
    ### end Alembic commands ###