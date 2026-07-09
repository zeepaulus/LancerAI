"""make job_match_results.job_id nullable for manual JD matching

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-06 00:01:00.000000

Allows POST /jobs/matches to persist component scores even when the JD
was provided as raw text (no corresponding job_listings row).
The FK constraint is preserved — non-NULL values must still reference
a valid job_listings.id.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: str | Sequence[str] | None = 'c3d4e5f6a7b8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Allow job_id to be NULL in job_match_results."""
    op.alter_column('job_match_results', 'job_id', nullable=True)


def downgrade() -> None:
    """Revert job_id to NOT NULL (requires no NULL rows to exist first)."""
    op.alter_column('job_match_results', 'job_id', nullable=False)
