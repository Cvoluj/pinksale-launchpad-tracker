"""initial project table

Revision ID: 4e3f612c384b
Revises: Cvoluj
Create Date: 2024-07-10 13:21:15.135522

"""
import sqlalchemy as sa
from alembic import op

from sqlalchemy.dialects import mysql

revision = '4e3f612c384b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('project',
    sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.String(length=768), nullable=False),
    sa.Column('url', sa.String(length=768), nullable=False),
    sa.Column('platform', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('website', sa.String(length=768), nullable=True),
    sa.Column('telegram', sa.String(length=768), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_project_updated_at'), 'project', ['updated_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_project_updated_at'), table_name='project')
    op.drop_table('project')
