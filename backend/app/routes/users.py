from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from app.models import UserCreate, User, RoleEnum
from app.services.supabase_service import supabase_service
from app.services.openai_service import openai_service
from app.auth import get_current_user, AuthUser
from typing import List
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

async def generate_initial_tasks_background(user_id: str, user_role: RoleEnum, user_email: str, auth_user_id: str):
    """Background task to generate initial tasks after user onboarding"""
    try:
        initial_tasks = await openai_service.generate_initial_tasks(
            user_role, 
            {"user_email": user_email, "user_role": user_role}
        )
        
        for task in initial_tasks:
            task["user_id"] = user_id
            task["auth_user_id"] = auth_user_id  # Add auth user ID for workspace isolation
            await supabase_service.create_task(task)
            
        logger.info(f"Successfully generated {len(initial_tasks)} initial tasks for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to generate initial tasks for user {user_id}: {e}")

@router.post("/onboard", response_model=User, status_code=status.HTTP_201_CREATED)
async def onboard_user(user_data: UserCreate, background_tasks: BackgroundTasks, current_user: AuthUser = Depends(get_current_user)):
    """
    Onboard a new user - creates user, AI agents, and schedules initial task generation
    """
    try:
        # Check if user already exists
        existing_user = await supabase_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user with auth_user_id
        user_dict = user_data.model_dump()
        user_dict["auth_user_id"] = current_user.auth_id  # Link to Supabase Auth user
        created_user = await supabase_service.create_user(user_dict)
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create a dedicated folder for the user
        try:
            user_workspace_path = f"workspace/users/{current_user.auth_id}"
            os.makedirs(user_workspace_path, exist_ok=True)
            logger.info(f"Created workspace for user {current_user.auth_id} at {user_workspace_path}")
        except OSError as e:
            logger.error(f"Failed to create workspace for user {current_user.auth_id}: {e}")
            # We might not want to fail the whole onboarding if directory creation fails,
            # but we should log it as a critical error.
            # Depending on requirements, we could raise an HTTPException here.
            pass
        
        user_id = created_user["id"]
        
        # Create AI agents for the roles the user didn't choose
        ai_roles = [role for role in RoleEnum if role != user_data.role]
        
        for ai_role in ai_roles:
            agent_data = {
                "user_id": user_id,
                "role": ai_role,
                "conversation_state": {
                    "initialized": True,
                    "messages": [],
                    "context": {"user_role": user_data.role}
                }
            }
            await supabase_service.create_agent(agent_data)
        
        # Schedule initial task generation in the background
        background_tasks.add_task(
            generate_initial_tasks_background,
            user_id,
            user_data.role,
            user_data.email,
            current_user.auth_id
        )
        
        return User(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to onboard user"
        )

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = await supabase_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.get("/email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """Get user by email"""
    try:
        user = await supabase_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        ) 