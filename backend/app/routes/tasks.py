from fastapi import APIRouter, HTTPException, status
from app.models import Task, TaskCreate, TaskUpdate, TaskStatusEnum
from app.services.supabase_service import supabase_service
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    try:
        # Validate user exists
        user = await supabase_service.get_user_by_id(str(task_data.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        task_dict = task_data.model_dump()
        created_task = await supabase_service.create_task(task_dict)
        
        if not created_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )
        
        return Task(**created_task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )

@router.get("/user/{user_id}", response_model=List[Task])
async def get_user_tasks(user_id: str, status: Optional[TaskStatusEnum] = None):
    """Get all tasks for a user, optionally filtered by status"""
    try:
        tasks = await supabase_service.get_tasks_by_user(user_id)
        
        # Filter by status if provided
        if status:
            tasks = [task for task in tasks if task.get("status") == status]
        
        return [Task(**task) for task in tasks]
        
    except Exception as e:
        logger.error(f"Error getting user tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user tasks"
        )

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    try:
        # Only include non-None fields in the update
        update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_task = await supabase_service.update_task(task_id, update_data)
        
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return Task(**updated_task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task"""
    try:
        # You'll need to add a delete method to supabase_service
        # For now, we'll return a placeholder
        return {"message": "Delete task endpoint - implement delete method in supabase_service"}
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )

@router.get("/role/{role}/user/{user_id}", response_model=List[Task])
async def get_tasks_by_role(role: str, user_id: str):
    """Get all tasks assigned to a specific role for a user"""
    try:
        all_tasks = await supabase_service.get_tasks_by_user(user_id)
        role_tasks = [task for task in all_tasks if task.get("assigned_to_role") == role]
        
        return [Task(**task) for task in role_tasks]
        
    except Exception as e:
        logger.error(f"Error getting tasks by role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tasks by role"
        ) 