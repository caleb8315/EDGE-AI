from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from typing import Dict, List, Optional, Any
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        # Only create client if we have valid credentials
        if SUPABASE_URL and SUPABASE_URL != "https://placeholder.supabase.co" and SUPABASE_KEY and SUPABASE_KEY != "placeholder_key":
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        else:
            self.client = None
            print("⚠️  Warning: Using placeholder Supabase credentials. Database operations will be mocked.")
        
        # In-memory stores for dev mode when Supabase creds are not provided
        self._mock_users = {}
        self._mock_agents = {}
        self._mock_tasks = {}
    
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
            self._mock_users[mock_user["id"]] = mock_user
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
            return self._mock_users.get(user_id)
        
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
            self._mock_agents[mock_agent["id"]] = mock_agent
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
        if not self.client:
            return [agent for agent in self._mock_agents.values() if agent["user_id"] == user_id]
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
            # Ensure user_id is stored as string for consistent comparisons
            task_data = {**task_data}
            if "user_id" in task_data:
                task_data["user_id"] = str(task_data["user_id"])

            mock_task = {
                **task_data,
                "id": str(uuid.uuid4()),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
            self._mock_tasks[mock_task["id"]] = mock_task
            logger.info(f"Mock: Created task {mock_task}")
            return mock_task
        
        try:
            # Only include columns that exist in the Supabase `tasks` table to avoid
            # PostgREST errors like PGRST204 when an unexpected column is sent.
            _allowed_cols = {
                "id",
                "user_id",
                "assigned_to_role",
                "description",
                "status",
                "resources",
                "created_at",
                "updated_at",
            }
            sanitized = {
                k: (str(v) if isinstance(v, UUID) else v)
                for k, v in task_data.items()
                if k in _allowed_cols
            }
            response = self.client.table("tasks").insert(sanitized).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    async def get_tasks_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        if not self.client:
            return [task for task in self._mock_tasks.values() if str(task["user_id"]) == str(user_id)]
        try:
            # Try to query with the user_id as-is first
            try:
                response = self.client.table("tasks").select("*").eq("user_id", user_id).execute()
            except Exception as uuid_error:
                # If it fails due to UUID format, try to find a valid UUID for this user
                # This handles cases where frontend passes non-UUID user identifiers
                logger.warning(f"UUID format error for user_id {user_id}: {uuid_error}")
                # For now, return empty list - in production you'd want to map user identifiers to UUIDs
                return []
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting tasks by user: {e}")
            raise
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        if not self.client:
            existing = self._mock_tasks.get(task_id)
            if not existing:
                return None
            existing.update(task_data)
            self._mock_tasks[task_id] = existing
            return existing
        try:
            # Supabase client needs plain JSON; convert UUIDs to strings
            sanitized = {k: (str(v) if isinstance(v, UUID) else v) for k, v in task_data.items()}
            response = self.client.table("tasks").update(sanitized).eq("id", task_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if not self.client:
            if task_id in self._mock_tasks:
                del self._mock_tasks[task_id]
                return True
            return False
        try:
            self.client.table("tasks").delete().eq("id", task_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            raise

    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company profile"""
        if not self.client:
            import uuid
            mock_company = {
                **company_data,
                "id": str(uuid.uuid4()),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
            # Store in _mock_companies dict which we create lazily
            if not hasattr(self, "_mock_companies"):
                self._mock_companies = {}
            self._mock_companies[mock_company["id"]] = mock_company
            logger.info(f"Mock: Created company {mock_company}")
            return mock_company

        try:
            # NOTE: The Supabase `companies` table may not yet have the extended
            # context columns (e.g. `company_info`, `product_overview`, etc.).
            # To avoid "PGRST204: column does not exist" errors we conservatively
            # whitelist only the core columns that are guaranteed to be present.
            _allowed_cols = {
                "id",
                "user_id",
                "name",
                "description",
                "industry",
                "stage",
                "company_info",
                "product_overview",
                "tech_stack",
                "go_to_market_strategy",
                "codebase_files",
                "created_at",
                "updated_at",
            }
            sanitized = {
                k: (str(v) if isinstance(v, UUID) else v)
                for k, v in company_data.items()
                if k in _allowed_cols
            }
            response = self.client.table("companies").insert(sanitized).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            raise

    async def get_company_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch company profile for a user"""
        if not self.client:
            if hasattr(self, "_mock_companies"):
                for comp in self._mock_companies.values():
                    if str(comp.get("user_id")) == str(user_id):
                        return comp
            return None
        try:
            # Fetch at most one matching row; avoid `.single()` so we don't raise
            # a 406 error when zero rows are found (PGRST116).
            response = (
                self.client.table("companies")
                .select("*")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting company by user: {e}")
            raise

    async def update_company(self, company_id: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update company"""
        if not self.client:
            if hasattr(self, "_mock_companies") and company_id in self._mock_companies:
                self._mock_companies[company_id].update(company_data)
                return self._mock_companies[company_id]
            return None
        try:
            # For the same reasons as in `create_company`, filter to recognized columns
            _allowed_cols = {
                "name",
                "description",
                "industry",
                "stage",
                "company_info",
                "product_overview",
                "tech_stack",
                "go_to_market_strategy",
                "codebase_files",
            }
            sanitized = {
                k: (str(v) if isinstance(v, UUID) else v)
                for k, v in company_data.items()
                if k in _allowed_cols
            }
            response = self.client.table("companies").update(sanitized).eq("id", company_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating company: {e}")
            raise

# Create a singleton instance
supabase_service = SupabaseService() 