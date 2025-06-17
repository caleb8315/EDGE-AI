from pathlib import Path
import os

__all__ = [
    "EDGE_ROOT",
    "get_user_workspace",
    "is_safe_path",
]

# Root of the EDGE workspace – override via env for tests / prod
EDGE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()
EDGE_ROOT.mkdir(parents=True, exist_ok=True)


def get_user_workspace(auth_user_id: str, *, create: bool = True) -> Path:
    """Return the absolute Path for a user workspace.

    The directory is `EDGE_ROOT/users/<auth_user_id>`.
    If *create* is True (default) the directory hierarchy is created if missing.
    """
    if not auth_user_id:
        raise ValueError("auth_user_id must be provided")

    user_dir = (EDGE_ROOT / "users" / auth_user_id).resolve()

    # Security: ensure we haven't escaped the root via traversal shenanigans
    if not is_safe_path(user_dir):
        raise ValueError("Invalid user directory path")

    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def is_safe_path(path: Path) -> bool:
    """Return True if *path* is inside ``EDGE_ROOT`` (no traversal)."""
    try:
        path.relative_to(EDGE_ROOT)
        return True
    except ValueError:
        return False 