"""PricingRule

Revision ID: b6ce341797a9
Revises: 33f12728c509
Create Date: 2023-08-04 15:03:27.551602

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6ce341797a9'
down_revision = '33f12728c509'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pricing_rule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('hourly_rate', sa.Float(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('package', sa.Column('space_id', sa.Integer(), nullable=False))
    op.add_column('package', sa.Column('creation_date', sa.DateTime(), nullable=False))
    op.create_foreign_key(None, 'package', 'space', ['space_id'], ['id'])
    op.drop_column('package', 'end_time')
    op.drop_column('package', 'start_time')
    op.drop_column('package', 'period')
    op.drop_column('package', 'price')
    op.add_column('space', sa.Column('capacity', sa.Integer(), nullable=True))
    op.drop_constraint('space_ibfk_1', 'space', type_='foreignkey')
    op.drop_column('space', 'package_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('space', sa.Column('package_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('space_ibfk_1', 'space', 'package', ['package_id'], ['id'])
    op.drop_column('space', 'capacity')
    op.add_column('package', sa.Column('price', mysql.FLOAT(), nullable=True))
    op.add_column('package', sa.Column('period', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('package', sa.Column('start_time', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('package', sa.Column('end_time', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'package', type_='foreignkey')
    op.drop_column('package', 'creation_date')
    op.drop_column('package', 'space_id')
    op.drop_table('pricing_rule')
    # ### end Alembic commands ###
