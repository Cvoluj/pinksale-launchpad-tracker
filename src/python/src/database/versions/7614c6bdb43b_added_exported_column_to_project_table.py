"""added exported column to Project table

Revision ID: 7614c6bdb43b
Revises: 13cfeb48ee75
Create Date: 2024-07-23 12:25:03.546294

"""
import sqlalchemy as sa
from alembic import op



revision = '7614c6bdb43b'
down_revision = '13cfeb48ee75'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('exported', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('project', 'exported')
