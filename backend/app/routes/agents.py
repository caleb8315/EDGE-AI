from fastapi import APIRouter, HTTPException, status
from app.models import Agent, ChatMessage, ChatResponse, RoleEnum
from app.services.supabase_service import supabase_service
from app.services.openai_service import openai_service
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import re, uuid
from app.agents.executor import get_tool_agent

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory cache to avoid hitting OpenAI on every page refresh
#  Keyed by user_id and stores {"timestamp": datetime, "payload": dict}
#  NOTE: This is a simple optimisation that works for a single-process server.
#  If you run multiple workers or deploy server-less, consider a shared cache
#  such as Redis or Supabase instead.
_SUGGESTIONS_CACHE: dict[str, Dict[str, Any]] = {}
_SUGGESTIONS_TTL = timedelta(minutes=5)

@router.get("/user/{user_id}", response_model=List[Agent])
async def get_user_agents(user_id: str):
    """Get all agents for a user"""
    try:
        agents = await supabase_service.get_agents_by_user(user_id)
        return [Agent(**agent) for agent in agents]
    except Exception as e:
        logger.error(f"Error getting user agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user agents"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_message: ChatMessage):
    """Send a message to an AI agent and get a response with enhanced intelligence"""
    try:
        # Get user to validate
        user = await supabase_service.get_user_by_id(str(chat_message.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all agents for inter-agent coordination
        agents = await supabase_service.get_agents_by_user(str(chat_message.user_id))
        target_agent = None
        other_agents = []
        
        for agent in agents:
            if agent["role"] == chat_message.role:
                target_agent = agent
            else:
                other_agents.append(agent)
        
        if not target_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {chat_message.role} agent found for this user"
            )
        
        # Build inter-agent coordination context
        other_agents_activity = {}
        for agent in other_agents:
            conv_state = agent.get("conversation_state", {})
            other_agents_activity[agent["role"]] = {
                "last_active": conv_state.get("timestamp", "unknown"),
                "message_count": conv_state.get("message_count", 0),
                "recent_topics": conv_state.get("topics_discussed", []),
                "status": "active" if conv_state.get("message_count", 0) > 0 else "initialized"
            }
        
        # Get conversation history from agent state
        conversation_state = target_agent.get("conversation_state", {})
        conversation_history = conversation_state.get("messages", [])
        
        # Add user message to history
        user_message_entry = {
            "message": chat_message.message,
            "is_from_user": True,
            "timestamp": datetime.now().isoformat()
        }
        conversation_history.append(user_message_entry)
        
        # ------------------------------------------------------------------
        # Heuristic task extraction: parse the latest user message and create
        # tasks for any actionable phrases. This guarantees that tasks are
        # logged even when the LLM doesn't explicitly flag them.
        # ------------------------------------------------------------------
        tasks_created: list[str] = []
        try:
            import re as _re, uuid as _uuid

            def _infer_role(_desc: str) -> str:
                _d = _desc.lower()
                if any(k in _d for k in ["ui", "interface", "frontend", "design"]):
                    return "CTO"
                if any(k in _d for k in ["marketing", "feedback", "survey", "campaign"]):
                    return "CMO"
                return "CEO"

            raw_msg = chat_message.message
            parts = _re.split(r"\band\b|[\n\u2022]", raw_msg)
            for part in parts:
                part = part.strip(" .")
                if not part:
                    continue
                desc: str | None = None
                # Look for modal phrases (need to / should / must / have to / please)
                if _re.search(r"\b(need to|should|must|have to|please)\b", part, _re.I):
                    desc = _re.sub(r"^(I|we)?\s*(need to|should|must|have to|please)\s*", "", part, flags=_re.I).strip()
                # Or imperative verb at the start (update, gather, etc.)
                elif _re.match(r"^(?:also\s+|then\s+)?(update|gather|create|build|write|design|implement|fix)\b", part, _re.I):
                    desc = part
                if desc:
                    task_payload = {
                        "id": str(_uuid.uuid4()),
                        "user_id": str(chat_message.user_id),
                        "assigned_to_role": _infer_role(desc),
                        "description": desc.capitalize(),
                        "status": "pending",
                    }
                    await supabase_service.create_task(task_payload)
                    tasks_created.append(desc.capitalize())
        except Exception as _heur_err:
            logger.warning(f"Heuristic task extraction failed: {_heur_err}")
        
        # ------------------------------------------------------------------
        # Heuristic task extraction: always create tasks when user message
        # clearly expresses an action, even if not tagged. Mirrors logic used
        # Enhanced user context
        enhanced_user_context = {
            "user_role": user["role"], 
            "user_email": user["email"],
            "startup_stage": "early" if len(conversation_history) < 10 else "growing",
            "team_size": len(agents) + 1,  # AI agents + human user
            "active_agents": len([a for a in agents if a.get("conversation_state", {}).get("message_count", 0) > 0])
        }
        
        # Get enhanced AI response
        ai_response = await openai_service.get_agent_response(
            agent_role=chat_message.role,
            user_message=chat_message.message,
            conversation_history=conversation_history,
            user_context=enhanced_user_context,
            other_agents_activity=other_agents_activity
        )
        
        # Add AI response to history
        ai_message_entry = {
            "message": ai_response["message"],
            "is_from_user": False,
            "timestamp": datetime.now().isoformat()
        }
        conversation_history.append(ai_message_entry)
        
        # Auto-create tasks if AI marks them using [[task:ROLE]] syntax
        try:
            task_matches = re.findall(r"\[\[task:(CEO|CTO|CMO)\]\](.+)", ai_response["message"], re.IGNORECASE)
            for role, desc in task_matches:
                task_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": str(chat_message.user_id),
                    "assigned_to_role": role.upper(),
                    "description": desc.strip(),
                    "status": "pending"
                }
                await supabase_service.create_task(task_data)
        except Exception as e:
            logger.warning(f"Failed to parse or create tasks from AI response: {e}")
        
        # Update agent conversation state with enhanced tracking
        updated_conversation_state = {
            **conversation_state,
            "messages": conversation_history,
            "last_updated": datetime.now().isoformat(),
            "message_count": ai_response["conversation_state"]["message_count"],
            "topics_discussed": ai_response["conversation_state"]["topics_discussed"],
            "sentiment": ai_response["conversation_state"]["sentiment"],
            "context_summary": f"Recent discussion about: {', '.join(ai_response['conversation_state']['topics_discussed'][:3])}"
        }
        
        await supabase_service.update_agent_conversation(
            target_agent["id"], 
            updated_conversation_state
        )
        
        # If we auto-created tasks, append a confirmation note to the assistant message
        final_message = ai_response["message"]
        if tasks_created:
            bullets = "\n".join(f"• {t}" for t in tasks_created)
            final_message += f"\n\nI've added the following tasks:\n{bullets}"

        return ChatResponse(
            agent_role=chat_message.role,
            message=final_message,
            conversation_state=updated_conversation_state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat with agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/{agent_id}/conversation")
async def get_agent_conversation(agent_id: str):
    """Get conversation history for an agent"""
    try:
        # This would require a direct agent lookup - you might want to add this to supabase_service
        # For now, we'll return a placeholder
        return {"message": "Conversation history endpoint - implement agent lookup by ID"}
    except Exception as e:
        logger.error(f"Error getting agent conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation history"
        )

@router.get("/user/{user_id}/status")
async def get_agents_status(user_id: str):
    """Get comprehensive status of all AI agents for a user"""
    try:
        # Get user to validate
        user = await supabase_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all agents
        agents = await supabase_service.get_agents_by_user(user_id)
        
        # Build comprehensive status
        agents_status = {}
        for agent in agents:
            conv_state = agent.get("conversation_state", {})
            agents_status[agent["role"]] = {
                "id": agent["id"],
                "role": agent["role"],
                "status": "active" if conv_state.get("message_count", 0) > 0 else "initialized",
                "message_count": conv_state.get("message_count", 0),
                "last_active": conv_state.get("timestamp", agent.get("created_at")),
                "recent_topics": conv_state.get("topics_discussed", []),
                "context_summary": conv_state.get("context_summary", f"AI {agent['role']} ready to assist"),
                "sentiment": conv_state.get("sentiment", "ready")
            }
        
        return {
            "user_role": user["role"],
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a.get("conversation_state", {}).get("message_count", 0) > 0]),
            "agents": agents_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agents status"
        )

@router.get("/user/{user_id}/suggestions")
async def get_proactive_suggestions(user_id: str):
    """Get proactive suggestions based on current activity and AI agent status"""
    try:
        # Get user to validate
        user = await supabase_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get agents status
        agents = await supabase_service.get_agents_by_user(user_id)
        
        # Get recent tasks for activity context
        tasks = await supabase_service.get_tasks_by_user(user_id)
        recent_tasks = tasks[:5]  # Last 5 tasks
        
        # Build activity context
        recent_activity = {
            "user_role": user["role"],
            "total_tasks": len(tasks),
            "pending_tasks": len([t for t in tasks if t.get("status") == "pending"]),
            "recent_task_topics": [t.get("description", "")[:50] for t in recent_tasks]
        }
        
        # Build AI agents status
        ai_agents_status = {}
        for agent in agents:
            conv_state = agent.get("conversation_state", {})
            ai_agents_status[agent["role"]] = {
                "activity_level": conv_state.get("message_count", 0),
                "recent_topics": conv_state.get("topics_discussed", []),
                "status": "active" if conv_state.get("message_count", 0) > 0 else "underutilized"
            }
        
        # -------------------------------------------------------------------
        # Try to serve cached suggestions if they are still fresh
        cached = _SUGGESTIONS_CACHE.get(user_id)
        now = datetime.utcnow()
        if cached and now - cached["timestamp"] < _SUGGESTIONS_TTL:
            return cached["payload"]

        # Generate fresh proactive suggestions via OpenAI
        suggestions = await openai_service.get_proactive_suggestions(
            user_role=RoleEnum(user["role"]),
            recent_activity=recent_activity,
            ai_agents_status=ai_agents_status,
        )
        
        # Attach the originating AI role to each suggestion for richer UI context
        ai_roles = [agent["role"] for agent in agents if agent["role"] != user["role"]]
        for idx, suggestion in enumerate(suggestions):
            # Cycle through available AI roles so we always have a from_agent label
            if isinstance(suggestion, dict):
                suggestion["from_agent"] = ai_roles[idx % len(ai_roles)] if ai_roles else None

        response_payload = {
            "user_id": user_id,
            "generated_at": "now",
            "suggestions": suggestions,
            "context": {
                "recent_activity": recent_activity,
                "ai_agents_status": ai_agents_status
            }
        }

        # Store in cache
        _SUGGESTIONS_CACHE[user_id] = {"timestamp": now, "payload": response_payload}

        return response_payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting proactive suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get proactive suggestions"
        ) 

@router.post("/chat-tools", response_model=ChatResponse)
async def chat_with_agent_tools(chat_message: ChatMessage):
    """Chat with agent using OpenAI function calling and EDGE tools"""
    try:
        agent = get_tool_agent()
        response_text = await agent.chat(chat_message.message, str(chat_message.user_id))

        # Return simple response; conversation_state is placeholder
        return ChatResponse(
            agent_role=chat_message.role,
            message=response_text,
            conversation_state={},
        )
    except Exception as e:
        logger.error(f"Error in chat_with_agent_tools: {e}")
        raise HTTPException(status_code=500, detail="Tool chat failed") 