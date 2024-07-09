"""initial project table

Revision ID: a2524a31e214
Revises: Cvoluj
Create Date: 2024-07-09 18:33:39.375935

"""
import sqlalchemy as sa
from alembic import op

from sqlalchemy.dialects import mysql

revision = 'a2524a31e214'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('project',
    sa.Column('id', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.String(length=768), nullable=False),
    sa.Column('url', sa.String(length=768), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=False),
    sa.Column('platform', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('website', sa.String(length=768), nullable=True),
    sa.Column('contact', mysql.JSON(), nullable=True),
    sa.Column('status', mysql.MEDIUMINT(unsigned=True), server_default=sa.text('0'), nullable=False),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_project_status'), 'project', ['status'], unique=False)
    op.create_index(op.f('ix_project_updated_at'), 'project', ['updated_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_project_updated_at'), table_name='project')
    op.drop_index(op.f('ix_project_status'), table_name='project')
    op.drop_table('project')
