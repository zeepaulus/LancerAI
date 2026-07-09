"""add schema improvements for analytics and LLM context

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-07-06 00:00:00.000000

Changes per table:
- cv_records:          + audit_score, optimization_mode, status
- interview_sessions:  + status, jd_snapshot, tts_voice, llm_model
- interview_transcripts: + turn_number, star_score, stt_confidence, latency_ms
- job_match_results:   + frequency_score, position_score, semantic_score
- job_listings:        + experience_level, job_type, updated_at
- llm_response_cache:  + expires_at
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: str | Sequence[str] | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add new columns to existing tables for analytics and LLM context."""

    # --- cv_records ---
    op.add_column('cv_records', sa.Column('audit_score', sa.Float(), nullable=True))
    op.add_column('cv_records', sa.Column('optimization_mode', sa.String(length=20), nullable=True))
    op.add_column('cv_records', sa.Column(
        'status', sa.String(length=20), server_default='extracted', nullable=False,
    ))

    # --- interview_sessions ---
    op.add_column('interview_sessions', sa.Column(
        'status', sa.String(length=20), server_default='completed', nullable=False,
    ))
    op.add_column('interview_sessions', sa.Column('jd_snapshot', sa.Text(), nullable=True))
    op.add_column('interview_sessions', sa.Column('tts_voice', sa.String(length=100), nullable=True))
    op.add_column('interview_sessions', sa.Column('llm_model', sa.String(length=128), nullable=True))

    # --- interview_transcripts ---
    op.add_column('interview_transcripts', sa.Column('turn_number', sa.Integer(), nullable=True))
    op.add_column('interview_transcripts', sa.Column('star_score', sa.JSON(), nullable=True))
    op.add_column('interview_transcripts', sa.Column('stt_confidence', sa.Float(), nullable=True))
    op.add_column('interview_transcripts', sa.Column('latency_ms', sa.Integer(), nullable=True))

    # --- job_match_results ---
    op.add_column('job_match_results', sa.Column('frequency_score', sa.Float(), nullable=True))
    op.add_column('job_match_results', sa.Column('position_score', sa.Float(), nullable=True))
    op.add_column('job_match_results', sa.Column('semantic_score', sa.Float(), nullable=True))

    # --- job_listings ---
    op.add_column('job_listings', sa.Column('experience_level', sa.String(length=20), nullable=True))
    op.add_column('job_listings', sa.Column('job_type', sa.String(length=20), nullable=True))
    op.add_column('job_listings', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # --- llm_response_cache ---
    op.add_column('llm_response_cache', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Remove all columns added in this migration."""

    # --- llm_response_cache ---
    op.drop_column('llm_response_cache', 'expires_at')

    # --- job_listings ---
    op.drop_column('job_listings', 'updated_at')
    op.drop_column('job_listings', 'job_type')
    op.drop_column('job_listings', 'experience_level')

    # --- job_match_results ---
    op.drop_column('job_match_results', 'semantic_score')
    op.drop_column('job_match_results', 'position_score')
    op.drop_column('job_match_results', 'frequency_score')

    # --- interview_transcripts ---
    op.drop_column('interview_transcripts', 'latency_ms')
    op.drop_column('interview_transcripts', 'stt_confidence')
    op.drop_column('interview_transcripts', 'star_score')
    op.drop_column('interview_transcripts', 'turn_number')

    # --- interview_sessions ---
    op.drop_column('interview_sessions', 'llm_model')
    op.drop_column('interview_sessions', 'tts_voice')
    op.drop_column('interview_sessions', 'jd_snapshot')
    op.drop_column('interview_sessions', 'status')

    # --- cv_records ---
    op.drop_column('cv_records', 'status')
    op.drop_column('cv_records', 'optimization_mode')
    op.drop_column('cv_records', 'audit_score')
