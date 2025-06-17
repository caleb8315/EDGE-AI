#!/usr/bin/env python3
"""
Script to clear all existing tasks from the database.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.supabase_service import supabase_service

async def clear_tasks():
    """Clear all tasks from the database."""
    if supabase_service.client:
        try:
            # Delete all existing tasks
            result = supabase_service.client.table('tasks').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f'Cleared {len(result.data) if result.data else 0} tasks from database')
        except Exception as e:
            print(f'Error clearing tasks: {e}')
    else:
        supabase_service._mock_tasks.clear()
        print('Cleared mock tasks')

if __name__ == "__main__":
    asyncio.run(clear_tasks()) 