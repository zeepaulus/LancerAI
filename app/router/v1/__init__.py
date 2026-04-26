"""API v1 routers.

Each module mounts a single ``APIRouter`` and is included from ``app.main``
under the ``/api/v1`` prefix.
"""

from app.router.v1 import (  # noqa: F401  re-exported for convenience
    auth_api,
    extraction_api,
    interview_api,
    job_matching_api,
    optimization_api,
)
