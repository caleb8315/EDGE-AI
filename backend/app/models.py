from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    CEO = "CEO"
    CTO = "CTO"
    CMO = "CMO"

class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Authentication Models
class AuthSignUp(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum

class AuthSignIn(BaseModel):
    email: EmailStr
    password: str

class AuthUser(BaseModel):
    id: str
    email: str
    created_at: str
    user_metadata: Dict[str, Any] = {}

class AuthResponse(BaseModel):
    user: AuthUser
    session: Dict[str, Any]

# User Models (Legacy - for backward compatibility)
class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum
    auth_user_id: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent Models
class AgentBase(BaseModel):
    user_id: UUID
    role: RoleEnum
    conversation_state: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Task Models
class TaskBase(BaseModel):
    user_id: UUID
    assigned_to_role: RoleEnum
    description: str
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    auth_user_id: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None

class Task(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str
    resources: List[str] | None = []

    class Config:
        from_attributes = True

# Chat Models
class ChatMessage(BaseModel):
    user_id: UUID
    role: RoleEnum
    message: str
    is_from_user: bool = True

class ChatResponse(BaseModel):
    agent_role: RoleEnum
    message: str
    conversation_state: Optional[Dict[str, Any]] = None

# Company Models
class CompanyBase(BaseModel):
    user_id: UUID
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None  # e.g., idea, prototype, launched
    company_info: Optional[str] = None  # Broader context about the company vision/mission
    product_overview: Optional[str] = None  # Short description of the main product
    tech_stack: Optional[str] = None  # Primary technologies being used or considered
    go_to_market_strategy: Optional[str] = None  # High-level GTM strategy statement
    codebase_files: Optional[List[str]] = None  # List of uploaded codebase file paths

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    codebase_files: List[str] | None = []

    class Config:
        from_attributes = True 