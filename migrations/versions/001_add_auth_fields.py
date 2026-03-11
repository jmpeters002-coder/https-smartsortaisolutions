"""Add email and auth fields to User model

Revision ID: 001
Revises: ded3212adaf0
Create Date: 2026-03-11 10:50:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision = '001'
down_revision = 'ded3212adaf0'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('email_verified_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('password_reset_token', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('password_reset_expires', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)


def downgrade():
    # Remove columns if rolling back
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email'))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('last_login')
        batch_op.drop_column('password_reset_expires')
        batch_op.drop_column('password_reset_token')
        batch_op.drop_column('email_verified_at')
        batch_op.drop_column('email_verified')
        batch_op.drop_column('is_active')
        batch_op.drop_column('name')
        batch_op.drop_column('email')
