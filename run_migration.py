#!/usr/bin/env python3
"""
Run the database migration to add auth_user_id columns.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.supabase_service import supabase_service

async def run_migration():
    """Add auth_user_id columns to the database."""
    if not supabase_service.client:
        print("No Supabase client available - skipping migration")
        return
    
    migration_sql = """
    -- Add auth_user_id column to users table
    ALTER TABLE public.users ADD COLUMN IF NOT EXISTS auth_user_id TEXT;

    -- Add auth_user_id column to tasks table  
    ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS auth_user_id TEXT;

    -- Create index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON public.users(auth_user_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_auth_user_id ON public.tasks(auth_user_id);
    """
    
    try:
        # Note: This won't work with the Python client - you need to run this in Supabase SQL Editor
        print("⚠️  You need to run this SQL manually in your Supabase Dashboard → SQL Editor:")
        print("\n" + "="*60)
        print(migration_sql)
        print("="*60 + "\n")
        print("After running the SQL, restart your backend server.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration()) 