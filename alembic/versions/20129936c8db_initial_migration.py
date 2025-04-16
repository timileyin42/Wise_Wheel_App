"""Initial migration

Revision ID: 20129936c8db
Revises: 
Create Date: 2025-04-16 10:17:46.585400

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20129936c8db'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraints before dropping the tables
    op.drop_constraint('rental_user_id_fkey', 'rental', type_='foreignkey')
    op.drop_constraint('rental_car_id_fkey', 'rental', type_='foreignkey')
    
    # Drop the tables after removing the constraints
    op.drop_table('user')
    op.drop_table('rental')
    op.drop_table('car')


def downgrade() -> None:
    # Recreate the user, rental, and car tables in case of a downgrade
    op.create_table('car',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('car_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('maker', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('model', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('price_per_day', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('availability', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('image_file', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('date_added', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='car_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('rental',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('total_amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('payment_status', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('car_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], name='rental_car_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='rental_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='rental_pkey')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('image_file', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('verification_token', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('token_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('username', name='user_username_key'),
    sa.UniqueConstraint('verification_token', name='user_verification_token_key')
    )

    # ### end Alembic commands ###
