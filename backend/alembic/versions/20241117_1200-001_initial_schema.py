"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create documents table with all fields."""
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('original_file_path', sa.String(length=500), nullable=False),
        sa.Column('formatted_file_path', sa.String(length=500), nullable=True),
        sa.Column('template_name', sa.String(length=100), nullable=False, server_default='gost_vkr'),
        sa.Column(
            'status',
            sa.Enum('uploaded', 'processing', 'completed', 'failed', name='documentstatus'),
            nullable=False,
            server_default='uploaded'
        ),
        sa.Column('structure_analysis', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)


def downgrade() -> None:
    """Drop documents table."""
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    # Drop enum type (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS documentstatus')
