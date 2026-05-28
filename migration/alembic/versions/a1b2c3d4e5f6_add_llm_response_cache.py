"""add_llm_response_cache

Revision ID: a1b2c3d4e5f6
Revises: 33189b3b2b5e
Create Date: 2026-05-27 17:53:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | Sequence[str] | None = '33189b3b2b5e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add llm_response_cache table for semantic response caching."""
    op.create_table(
        'llm_response_cache',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column(
            'prompt_hash', sa.String(length=64), nullable=False,
            comment='SHA-256 hex of the full prompt text',
        ),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column(
            'prompt_embedding', sa.JSON(), nullable=False,
            comment='Float32 embedding vector of prompt_text',
        ),
        sa.Column(
            'model_name', sa.String(length=128), nullable=False,
            comment='LLM model name used to generate the response',
        ),
        sa.Column(
            'backend', sa.String(length=32), nullable=False,
            comment='nvidia | groq | ollama',
        ),
        sa.Column(
            'triggered_by_user_id', sa.String(length=36), nullable=True,
            comment='user.id who triggered the original LLM call (analytics only)',
        ),
        sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.text('now()'), nullable=False,
        ),
        sa.Column(
            'last_accessed_at', sa.DateTime(timezone=True),
            server_default=sa.text('now()'), nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_llm_response_cache')),
    )
    op.create_index(
        op.f('ix_llm_response_cache_prompt_hash'),
        'llm_response_cache', ['prompt_hash'], unique=False,
    )
    op.create_index(
        op.f('ix_llm_response_cache_triggered_by_user_id'),
        'llm_response_cache', ['triggered_by_user_id'], unique=False,
    )


def downgrade() -> None:
    """Drop llm_response_cache table."""
    op.drop_index(
        op.f('ix_llm_response_cache_triggered_by_user_id'),
        table_name='llm_response_cache',
    )
    op.drop_index(
        op.f('ix_llm_response_cache_prompt_hash'),
        table_name='llm_response_cache',
    )
    op.drop_table('llm_response_cache')
