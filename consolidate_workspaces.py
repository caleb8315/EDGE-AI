import asyncio
import logging
import os
import shutil
import sys
import uuid
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from app.services.supabase_service import supabase_service
except ImportError as e:
    logging.error(f"Failed to import supabase_service: {e}")
    logging.error(
        "Please ensure you are running this script from the project root directory "
        "and that backend dependencies are installed."
    )
    sys.exit(1)

WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", Path.cwd() / "workspace")).resolve()
USERS_DIR = WORKSPACE_ROOT / "users"

# Legacy directory from a previous migration
OLD_COMPLETED_TASKS_DIR = WORKSPACE_ROOT / "completed_tasks"


def is_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError):
        return False


async def consolidate_workspaces():
    """
    Consolidates old user workspace directories into the new `workspace/users/<auth_user_id>` structure.
    """
    logging.info("Starting workspace consolidation...")
    if not supabase_service.client:
        logging.error(
            "Supabase client not initialized. Check your .env file in the backend directory."
        )
        return

    # 1. Fetch all users to map db_id to auth_id
    logging.info("Fetching user data from Supabase...")
    try:
        response = (
            supabase_service.client.table("users").select("id, auth_user_id").execute()
        )
        if not response.data:
            logging.warning("No users found in the database. Nothing to migrate.")
            return
        user_map = {
            user["id"]: user["auth_user_id"]
            for user in response.data
            if user.get("auth_user_id")
        }
        logging.info(f"Found {len(user_map)} users with auth_user_id.")
    except Exception as e:
        logging.error(f"Failed to fetch users from Supabase: {e}")
        return

    # Ensure the main `users` directory exists
    USERS_DIR.mkdir(exist_ok=True)

    # 2. Process legacy directories directly in WORKSPACE_ROOT
    logging.info(f"Scanning for legacy user directories in {WORKSPACE_ROOT}...")
    migrated_count = 0
    for item in WORKSPACE_ROOT.iterdir():
        if item.is_dir() and is_uuid(item.name):
            db_id = item.name
            if db_id in user_map:
                auth_id = user_map[db_id]
                logging.info(
                    f"Found legacy directory for user {db_id} (auth_id: {auth_id})."
                )
                target_dir = USERS_DIR / auth_id
                target_dir.mkdir(exist_ok=True)

                # Move contents
                for content_item in item.iterdir():
                    dest_path = target_dir / content_item.name
                    try:
                        shutil.move(str(content_item), str(dest_path))
                        logging.info(
                            f"Moved {content_item.relative_to(WORKSPACE_ROOT)} to {dest_path.relative_to(WORKSPACE_ROOT)}"
                        )
                    except shutil.Error as e:
                        logging.warning(
                            f"Could not move {content_item.name}: {e}. It might already exist in the destination. Skipping."
                        )

                # Remove old directory if empty
                try:
                    item.rmdir()
                    logging.info(f"Removed empty legacy directory: {item.name}")
                    migrated_count += 1
                except OSError:
                    logging.warning(
                        f"Could not remove directory {item.name}. It might not be empty."
                    )
            else:
                logging.warning(
                    f"Found UUID directory '{db_id}' but no matching user in database. Skipping."
                )

    # 3. Process legacy `completed_tasks/<user_id>` directories
    if OLD_COMPLETED_TASKS_DIR.exists():
        logging.info(
            f"Scanning for legacy completed_tasks directories in {OLD_COMPLETED_TASKS_DIR}..."
        )
        for item in OLD_COMPLETED_TASKS_DIR.iterdir():
            if item.is_dir() and is_uuid(item.name):
                db_id = item.name
                if db_id in user_map:
                    auth_id = user_map[db_id]
                    logging.info(
                        f"Found legacy completed_tasks for user {db_id} (auth_id: {auth_id})."
                    )
                    target_dir = (
                        USERS_DIR / auth_id / "completed_tasks"
                    )  # Put them in a subfolder
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Move contents
                    for content_item in item.iterdir():
                        dest_path = target_dir / content_item.name
                        try:
                            shutil.move(str(content_item), str(dest_path))
                            logging.info(
                                f"Moved {content_item.relative_to(WORKSPACE_ROOT)} to {dest_path.relative_to(WORKSPACE_ROOT)}"
                            )
                        except shutil.Error as e:
                            logging.warning(
                                f"Could not move {content_item.name}: {e}. It might already exist in the destination. Skipping."
                            )

                    # Remove old user directory
                    try:
                        item.rmdir()
                        logging.info(f"Removed empty legacy directory: {item.name}")
                    except OSError:
                        logging.warning(
                            f"Could not remove directory {item.name}. It might not be empty."
                        )
        # Try to remove the top-level completed_tasks dir if empty
        try:
            OLD_COMPLETED_TASKS_DIR.rmdir()
            logging.info(f"Removed empty legacy directory: {OLD_COMPLETED_TASKS_DIR.name}")
        except OSError:
            logging.warning(
                f"Could not remove directory {OLD_COMPLETED_TASKS_DIR.name}. It might not be empty."
            )

    logging.info(
        f"Consolidation complete. Processed {migrated_count} legacy user directories."
    )


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(consolidate_workspaces()) 