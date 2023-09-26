"""Your Space Tables

Revision ID: 84252ce7c1e5
Revises: 
Create Date: 2023-08-02 15:22:52.769029

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '84252ce7c1e5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('creation_date', sa.DateTime(), nullable=False))
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('user', sa.Column('is_locked', sa.Boolean(), nullable=False))
    op.alter_column('user', 'rank',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'rank',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.drop_column('user', 'is_locked')
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'last_login')
    op.drop_column('user', 'creation_date')
    # ### end Alembic commands ###
