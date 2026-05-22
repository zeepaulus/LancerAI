"""add missing fk indexes

Revision ID: 33189b3b2b5e
Revises: 3048af82dd00
Create Date: 2026-05-12 23:00:56.604259

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '33189b3b2b5e'
down_revision: str | Sequence[str] | None = '3048af82dd00'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_interview_sessions_cv_id'), 'interview_sessions', ['cv_id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_job_listing_id'), 'interview_sessions', ['job_listing_id'], unique=False)
    op.create_index(op.f('ix_job_match_results_cv_id'), 'job_match_results', ['cv_id'], unique=False)
    op.create_index(op.f('ix_job_match_results_job_id'), 'job_match_results', ['job_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_job_match_results_job_id'), table_name='job_match_results')
    op.drop_index(op.f('ix_job_match_results_cv_id'), table_name='job_match_results')
    op.drop_index(op.f('ix_interview_sessions_job_listing_id'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_cv_id'), table_name='interview_sessions')
