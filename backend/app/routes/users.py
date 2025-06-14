from fastapi import APIRouter, HTTPException, status
from app.models import UserCreate, User, RoleEnum
from app.services.supabase_service import supabase_service
from app.services.openai_service import openai_service
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/onboard", response_model=User, status_code=status.HTTP_201_CREATED)
async def onboard_user(user_data: UserCreate):
    """
    Onboard a new user - creates user, AI agents, and initial tasks
    """
    try:
        # Check if user already exists
        existing_user = await supabase_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        user_dict = user_data.model_dump()
        created_user = await supabase_service.create_user(user_dict)
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
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
        
        # Generate initial tasks for AI agents
        try:
            initial_tasks = await openai_service.generate_initial_tasks(
                user_data.role, 
                {"user_email": user_data.email, "user_role": user_data.role}
            )
            
            for task in initial_tasks:
                task["user_id"] = user_id
                await supabase_service.create_task(task)
                
        except Exception as e:
            logger.warning(f"Failed to generate initial tasks: {e}")
            # Don't fail the onboarding if task generation fails
        
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