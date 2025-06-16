from fastapi import APIRouter, HTTPException, status, Body
from app.models import CompanyCreate, Company
from app.services.supabase_service import supabase_service
from app.services.openai_service import openai_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(company_data: CompanyCreate):
    """Create company profile"""
    try:
        created = await supabase_service.create_company(company_data.model_dump())
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create company")
        # Propagate context to user agents
        try:
            agents = await supabase_service.get_agents_by_user(created["user_id"])
            for agent in agents:
                conversation_state = agent.get("conversation_state") or {}
                context = conversation_state.get("context", {})
                context.update({"company": created})
                conversation_state["context"] = context
                await supabase_service.update_agent_conversation(agent["id"], conversation_state)
        except Exception as e:
            logger.warning(f"Failed to propagate company context to agents: {e}")

        return Company(**created)
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(status_code=500, detail="Failed to create company")

@router.get("/user/{user_id}", response_model=Company | None)
async def get_company_by_user(user_id: str):
    try:
        company = await supabase_service.get_company_by_user(user_id)
        return Company(**company) if company else None
    except Exception as e:
        logger.error(f"Error fetching company: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company")

@router.put("/{company_id}", response_model=Company)
async def update_company(company_id: str, company_data: dict = Body(...)):
    try:
        updated = await supabase_service.update_company(company_id, company_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Company not found")
        # Propagate updated context to user agents
        try:
            user_id = updated["user_id"]
            agents = await supabase_service.get_agents_by_user(user_id)
            for agent in agents:
                conversation_state = agent.get("conversation_state") or {}
                context = conversation_state.get("context", {})
                context.update({"company": updated})
                conversation_state["context"] = context
                await supabase_service.update_agent_conversation(agent["id"], conversation_state)
        except Exception as e:
            logger.warning(f"Failed to propagate updated company context: {e}")

        return Company(**updated)
    except Exception as e:
        logger.error(f"Error updating company: {e}")
        raise HTTPException(status_code=500, detail="Failed to update company")

# AI suggestions endpoint

@router.post("/suggest", status_code=status.HTTP_200_OK)
async def suggest_company_context(payload: dict = Body(...)):
    """Generate AI suggestions for company context fields."""
    try:
        company_name = payload.get("name", "Your Startup")
        description = payload.get("description", "")
        suggestions = await openai_service.generate_company_context_suggestions(company_name, description)
        return suggestions
    except Exception as e:
        logger.error(f"Error generating company context suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions") 