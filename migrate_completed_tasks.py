#!/usr/bin/env python3
"""
Migration script to move existing completed tasks into user-specific folders.
Run this once to organize existing completed_tasks files by user.
"""

import os
import sys
from pathlib import Path
import shutil
import asyncio

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.supabase_service import supabase_service

WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()
COMPLETED_TASKS_DIR = WORKSPACE_ROOT / "completed_tasks"


async def migrate_completed_tasks():
    """Move existing completed tasks into user-specific folders."""
    print(f"Checking workspace: {WORKSPACE_ROOT}")
    
    if not COMPLETED_TASKS_DIR.exists():
        print("No completed_tasks folder found. Nothing to migrate.")
        return
    
    # Get all task files that are directly in completed_tasks/ (not in subfolders)
    task_files = []
    for item in COMPLETED_TASKS_DIR.iterdir():
        if item.is_file() and item.name.endswith(('.txt', '.py', '.md')):
            task_files.append(item)
    
    if not task_files:
        print("No task files found to migrate.")
        return
    
    print(f"Found {len(task_files)} task files to migrate")
    
    # Get all tasks from database to map task IDs to user IDs
    if supabase_service.client:
        try:
            response = supabase_service.client.table("tasks").select("id, user_id").execute()
            task_mapping = {task["id"]: task["user_id"] for task in response.data}
        except Exception as e:
            print(f"Failed to fetch tasks from database: {e}")
            task_mapping = {}
    else:
        # Use mock data if available
        task_mapping = {task["id"]: task["user_id"] for task in supabase_service._mock_tasks.values()}
    
    migrated_count = 0
    
    for task_file in task_files:
        # Extract task ID from filename (assuming format: {task_id}.{ext})
        task_id = task_file.stem
        
        if task_id in task_mapping:
            user_id = task_mapping[task_id]
            
            # Create user-specific directory
            user_dir = COMPLETED_TASKS_DIR / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Move file to user directory
            new_path = user_dir / task_file.name
            
            if not new_path.exists():
                shutil.move(str(task_file), str(new_path))
                print(f"Moved {task_file.name} -> {user_id}/{task_file.name}")
                migrated_count += 1
            else:
                print(f"File {new_path} already exists, skipping")
        else:
            print(f"No user mapping found for task {task_id}, leaving in place")
    
    print(f"Migration complete! Moved {migrated_count} files into user-specific folders.")


if __name__ == "__main__":
    asyncio.run(migrate_completed_tasks()) 