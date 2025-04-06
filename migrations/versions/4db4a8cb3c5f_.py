"""empty message

Revision ID: 4db4a8cb3c5f
Revises: 
Create Date: 2025-04-06 19:56:08.521088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4db4a8cb3c5f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('car',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('maker', sa.String(length=100), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('price_per_day', sa.Float(), nullable=False),
    sa.Column('availability', sa.Boolean(), nullable=True),
    sa.Column('image_file', sa.String(length=20), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('verification_token', sa.String(length=120), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username'),
    sa.UniqueConstraint('verification_token')
    )
    op.create_table('rental',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('payment_status', sa.Boolean(), nullable=True),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rental')
    op.drop_table('user')
    op.drop_table('car')
    # ### end Alembic commands ###
