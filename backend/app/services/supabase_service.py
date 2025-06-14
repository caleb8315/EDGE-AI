from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        # Only create client if we have valid credentials
        if SUPABASE_URL and SUPABASE_URL != "https://placeholder.supabase.co" and SUPABASE_KEY and SUPABASE_KEY != "placeholder_key":
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        else:
            self.client = None
            print("⚠️  Warning: Using placeholder Supabase credentials. Database operations will be mocked.")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in the database"""
        if not self.client:
            # Mock response for development
            import uuid
            mock_user = {
                **user_data,
                "id": str(uuid.uuid4()),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            logger.info(f"Mock: Created user {mock_user}")
            return mock_user
        
        try:
            response = self.client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if not self.client:
            logger.info(f"Mock: Get user by email {email} - returning None")
            return None
        
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.client:
            logger.info(f"Mock: Get user by ID {user_id} - returning None")
            return None
        
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        if not self.client:
            import uuid
            mock_agent = {
                **agent_data,
                "id": str(uuid.uuid4()),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            logger.info(f"Mock: Created agent {mock_agent}")
            return mock_agent
        
        try:
            response = self.client.table("agents").insert(agent_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            raise
    
    async def get_agents_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a user"""
        try:
            response = self.client.table("agents").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting agents by user: {e}")
            raise
    
    async def update_agent_conversation(self, agent_id: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent conversation state"""
        try:
            response = self.client.table("agents").update({
                "conversation_state": conversation_state
            }).eq("id", agent_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating agent conversation: {e}")
            raise
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        if not self.client:
            import uuid
            mock_task = {
                **task_data,
                "id": str(uuid.uuid4()),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            logger.info(f"Mock: Created task {mock_task}")
            return mock_task
        
        try:
            response = self.client.table("tasks").insert(task_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    async def get_tasks_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        try:
            response = self.client.table("tasks").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting tasks by user: {e}")
            raise
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        try:
            response = self.client.table("tasks").update(task_data).eq("id", task_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise

# Create a singleton instance
supabase_service = SupabaseService() 