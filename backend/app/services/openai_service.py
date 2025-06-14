from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.models import RoleEnum
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        if OPENAI_API_KEY and OPENAI_API_KEY != "sk-placeholder_key":
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None
            print("⚠️  Warning: Using placeholder OpenAI API key. AI responses will be mocked.")
        
        # Enhanced role-specific prompts with startup expertise
        self.role_prompts = {
            RoleEnum.CEO: """You are an experienced AI CEO assistant with deep startup expertise. Your personality is strategic, visionary, and decisive.

CORE RESPONSIBILITIES:
- Vision & Strategy: Define company direction, mission, values
- Leadership: Team building, culture, decision-making frameworks
- Fundraising: Investor relations, pitch development, financial planning
- Business Development: Partnerships, market positioning, competitive analysis
- Operations: High-level process optimization, KPI tracking

EXPERTISE AREAS:
- Startup methodologies (Lean Startup, Design Thinking, OKRs)
- Fundraising stages (Pre-seed, Seed, Series A+)
- Market analysis and competitive intelligence
- Leadership and team dynamics
- Financial modeling and unit economics
- Go-to-market strategy

COMMUNICATION STYLE:
- Strategic and big-picture focused
- Ask probing questions about market fit and scalability
- Reference successful startup case studies
- Balance optimism with realistic assessment
- Push for measurable outcomes and clear KPIs

INTER-AGENT COORDINATION:
- Collaborate with CTO on technical feasibility of business goals
- Work with CMO on brand positioning and market strategy
- Ensure all initiatives align with overall company vision
- Prioritize cross-functional initiatives

Always consider: What's the strategic implication? How does this scale? What's the ROI?""",

            RoleEnum.CTO: """You are a seasoned AI CTO assistant with extensive technical and product expertise. Your personality is analytical, pragmatic, and innovation-focused.

CORE RESPONSIBILITIES:
- Technical Architecture: System design, scalability, security
- Product Development: MVP planning, technical roadmap, feature prioritization
- Team Building: Technical hiring, mentoring, engineering culture
- Technology Strategy: Stack decisions, tool selection, technical debt management
- Data & Analytics: Infrastructure, data pipelines, technical insights

EXPERTISE AREAS:
- Modern tech stacks (React/Next.js, Python/FastAPI, cloud platforms)
- Startup technical patterns (microservices, serverless, containers)
- Product development methodologies (Agile, Scrum, continuous deployment)
- Technical scaling challenges and solutions
- Security best practices and compliance
- AI/ML integration and data architecture

COMMUNICATION STYLE:
- Technical but accessible to non-technical stakeholders
- Focus on practical implementation and tradeoffs
- Suggest specific tools, frameworks, and approaches
- Consider technical debt and long-term maintainability
- Emphasize data-driven decision making

INTER-AGENT COORDINATION:
- Translate CEO's vision into technical requirements
- Support CMO with technical capabilities for marketing tools
- Ensure technical decisions align with business objectives
- Provide realistic timelines and resource estimates

Always consider: Is this technically feasible? How will this scale? What are the security implications?""",

            RoleEnum.CMO: """You are a growth-focused AI CMO assistant with deep marketing and customer acquisition expertise. Your personality is creative, data-driven, and customer-obsessed.

CORE RESPONSIBILITIES:
- Growth Strategy: Customer acquisition, retention, viral coefficients
- Brand Development: Positioning, messaging, content strategy
- Marketing Channels: SEO, content, social, paid acquisition, partnerships
- Customer Research: User personas, market research, feedback loops
- Performance Marketing: Analytics, attribution, optimization, funnel analysis

EXPERTISE AREAS:
- Digital marketing channels and attribution models
- Content marketing and SEO strategies
- Social media and community building
- Product marketing and positioning
- Growth hacking and experimentation
- Customer journey mapping and conversion optimization

COMMUNICATION STYLE:
- Creative but data-backed suggestions
- Focus on customer empathy and user experience
- Propose specific tactics and experiments
- Reference successful marketing case studies
- Emphasize measurable growth metrics

INTER-AGENT COORDINATION:
- Align with CEO on brand positioning and market strategy
- Work with CTO on technical implementation of marketing tools
- Ensure marketing efforts support overall business objectives
- Coordinate product launches and feature announcements

Always consider: Who is our target customer? What's the customer acquisition cost? How can we improve retention?"""
        }
        
        # Enhanced context builders for each role
        self.context_builders = {
            RoleEnum.CEO: self._build_ceo_context,
            RoleEnum.CTO: self._build_cto_context,
            RoleEnum.CMO: self._build_cmo_context,
        }
    
    def _build_ceo_context(self, user_context: Dict[str, Any], conversation_state: Dict[str, Any]) -> str:
        """Build strategic context for CEO responses"""
        context_parts = ["STRATEGIC CONTEXT:"]
        
        if user_context.get("user_role"):
            context_parts.append(f"- User Role: {user_context['user_role']} (your business partner)")
        
        # Add business stage context
        message_count = conversation_state.get("message_count", 0)
        if message_count < 5:
            context_parts.append("- Company Stage: Early stage, focus on fundamentals")
        else:
            context_parts.append("- Company Stage: Active development, scaling considerations")
        
        context_parts.extend([
            "- Priority Areas: Vision clarity, market validation, team alignment",
            "- Key Questions: Product-market fit, competitive advantage, scalability",
            "- Success Metrics: User growth, revenue potential, team productivity"
        ])
        
        return "\n".join(context_parts)
    
    def _build_cto_context(self, user_context: Dict[str, Any], conversation_state: Dict[str, Any]) -> str:
        """Build technical context for CTO responses"""
        context_parts = ["TECHNICAL CONTEXT:"]
        
        if user_context.get("user_role"):
            context_parts.append(f"- User Role: {user_context['user_role']} (your business partner)")
        
        # Add technical stage context
        message_count = conversation_state.get("message_count", 0)
        if message_count < 5:
            context_parts.append("- Dev Stage: MVP planning, architecture decisions")
        else:
            context_parts.append("- Dev Stage: Active development, optimization focus")
        
        context_parts.extend([
            "- Tech Stack: Modern web (React/Next.js, Python/FastAPI, cloud-native)",
            "- Priority Areas: Scalable architecture, rapid prototyping, data infrastructure",
            "- Key Decisions: Technology choices, team structure, development process",
            "- Success Metrics: Development velocity, system reliability, technical debt"
        ])
        
        return "\n".join(context_parts)
    
    def _build_cmo_context(self, user_context: Dict[str, Any], conversation_state: Dict[str, Any]) -> str:
        """Build marketing context for CMO responses"""
        context_parts = ["MARKETING CONTEXT:"]
        
        if user_context.get("user_role"):
            context_parts.append(f"- User Role: {user_context['user_role']} (your business partner)")
        
        # Add marketing stage context
        message_count = conversation_state.get("message_count", 0)
        if message_count < 5:
            context_parts.append("- Marketing Stage: Brand foundation, early customer research")
        else:
            context_parts.append("- Marketing Stage: Growth experiments, channel optimization")
        
        context_parts.extend([
            "- Target Market: Early-stage startup tools and services",
            "- Priority Areas: Brand positioning, customer acquisition, growth metrics",
            "- Key Channels: Content marketing, social media, partnerships, SEO",
            "- Success Metrics: Customer acquisition cost, lifetime value, engagement"
        ])
        
        return "\n".join(context_parts)
    
    async def get_agent_response(
        self, 
        agent_role: RoleEnum, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        other_agents_activity: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get response from AI agent based on role with enhanced context"""
        if not self.client:
            # Enhanced mock responses
            mock_responses = {
                RoleEnum.CEO: f"As your AI CEO partner, I'm analyzing '{user_message}' from a strategic perspective. Key considerations: market opportunity, competitive positioning, and scalability. What's our target market size and how does this align with our 6-month milestones? (Mock response - no OpenAI key configured)",
                
                RoleEnum.CTO: f"From a technical standpoint on '{user_message}': I recommend we consider the architecture implications and technical feasibility. What's the expected user load and data requirements? Should we prototype this first or integrate with existing systems? (Mock response - no OpenAI key configured)",
                
                RoleEnum.CMO: f"Great question about '{user_message}'. From a growth perspective, let's think about our customer acquisition strategy. Who's our ideal customer profile and what channels should we prioritize? I'd suggest A/B testing this approach. (Mock response - no OpenAI key configured)"
            }
            
            return {
                "agent_role": agent_role,
                "message": mock_responses.get(agent_role, "Enhanced mock AI response"),
                "conversation_state": {
                    "last_message": mock_responses.get(agent_role, "Enhanced mock AI response"),
                    "message_count": len(conversation_history) + 1 if conversation_history else 1,
                    "context": user_context,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        try:
            # Build enhanced conversation context
            messages = [
                {"role": "system", "content": self.role_prompts[agent_role]}
            ]
            
            # Add role-specific context
            if user_context:
                context_builder = self.context_builders.get(agent_role)
                if context_builder:
                    conversation_state = conversation_history[-1] if conversation_history else {}
                    enhanced_context = context_builder(user_context, conversation_state)
                    messages.append({"role": "system", "content": enhanced_context})
            
            # Add inter-agent coordination context
            if other_agents_activity:
                coordination_context = f"TEAM COORDINATION:\n{json.dumps(other_agents_activity, indent=2)}"
                messages.append({"role": "system", "content": coordination_context})
            
            # Add conversation history with enhanced context
            if conversation_history:
                for msg in conversation_history[-8:]:  # Last 8 messages for context
                    messages.append({
                        "role": "user" if msg.get("is_from_user") else "assistant",
                        "content": msg.get("message", "")
                    })
            
            # Add current user message with proactive instruction
            enhanced_user_message = f"{user_message}\n\nPLEASE PROVIDE: Direct answer, specific recommendations, and one proactive suggestion for what we should consider next."
            messages.append({"role": "user", "content": enhanced_user_message})
            
            # Get response from OpenAI with enhanced parameters
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=600,  # Increased for more detailed responses
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            agent_message = response.choices[0].message.content
            
            return {
                "agent_role": agent_role,
                "message": agent_message,
                "conversation_state": {
                    "last_message": agent_message,
                    "message_count": len(conversation_history) + 1 if conversation_history else 1,
                    "context": user_context,
                    "timestamp": datetime.now().isoformat(),
                    "topics_discussed": self._extract_topics(user_message),
                    "sentiment": "engaged"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            raise
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract key topics from user message for context tracking"""
        # Simple keyword extraction - could be enhanced with NLP
        keywords = []
        startup_terms = ["mvp", "product", "market", "users", "growth", "revenue", "funding", "team", "strategy", "tech", "marketing", "customers", "analytics", "data", "ai", "api", "design", "launch", "scale"]
        
        message_lower = message.lower()
        for term in startup_terms:
            if term in message_lower:
                keywords.append(term)
        
        return keywords[:5]  # Return top 5 relevant topics
    
    async def generate_initial_tasks(self, user_role: RoleEnum, user_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate comprehensive initial tasks for AI agents based on user's role"""
        if not self.client:
            # Enhanced mock tasks with more specificity
            enhanced_mock_tasks = {
                RoleEnum.CEO: [
                    "Define company vision, mission, and core values statement",
                    "Conduct market size analysis and competitive landscape research",
                    "Create initial OKRs (Objectives and Key Results) framework",
                    "Develop investor pitch deck outline with key metrics"
                ],
                RoleEnum.CTO: [
                    "Design scalable system architecture for MVP development",
                    "Choose optimal technology stack based on team skills and requirements",
                    "Set up development environment with CI/CD pipeline",
                    "Create technical roadmap with security and performance considerations"
                ],
                RoleEnum.CMO: [
                    "Develop comprehensive brand identity and messaging framework",
                    "Create customer persona profiles with research methodology", 
                    "Design content marketing strategy with SEO optimization",
                    "Set up analytics infrastructure and growth tracking systems"
                ]
            }
            
            ai_roles = [role for role in RoleEnum if role != user_role]
            tasks = []
            
            for ai_role in ai_roles:
                role_tasks = enhanced_mock_tasks.get(ai_role, ["Sample enhanced task for " + ai_role.value])
                for description in role_tasks:
                    tasks.append({
                        "assigned_to_role": ai_role,
                        "description": description,
                        "status": "pending",
                        "priority": "high" if "MVP" in description or "framework" in description else "medium"
                    })
            
            return tasks
        
        try:
            # Define which roles need tasks based on user's role
            ai_roles = [role for role in RoleEnum if role != user_role]
            
            tasks = []
            for ai_role in ai_roles:
                # Enhanced prompt for task generation
                prompt = f"""As an expert {ai_role.value} for a startup where the founder is the {user_role.value}, 
                generate 3-4 high-priority, specific, and actionable initial tasks.

                Context: {json.dumps(user_context, indent=2) if user_context else 'New startup, early validation stage'}

                Focus on tasks that:
                1. Are immediately actionable and measurable
                2. Support the {user_role.value}'s goals and complement their role
                3. Follow startup best practices and methodologies
                4. Can be completed within 1-2 weeks
                5. Have clear success criteria

                Format: Return only the task descriptions, one per line, without numbering.
                Make each task specific with concrete deliverables."""
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.role_prompts[ai_role]},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.6
                )
                
                task_descriptions = response.choices[0].message.content.strip().split('\n')
                
                for i, description in enumerate(task_descriptions):
                    if description.strip():
                        tasks.append({
                            "assigned_to_role": ai_role,
                            "description": description.strip(),
                            "status": "pending",
                            "priority": "high" if i < 2 else "medium",  # First 2 tasks are high priority
                            "estimated_hours": 8 if "research" in description.lower() or "analysis" in description.lower() else 4
                        })
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error generating initial tasks: {e}")
            raise
    
    async def get_proactive_suggestions(
        self,
        user_role: RoleEnum,
        recent_activity: Dict[str, Any],
        ai_agents_status: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on current activity and context"""
        if not self.client:
            return [
                {
                    "type": "collaboration",
                    "message": f"As a {user_role.value}, consider syncing with your AI team on current priorities",
                    "action": "schedule_team_sync",
                    "priority": "medium"
                }
            ]
        
        try:
            # This would be called periodically to generate proactive insights
            prompt = f"""As a startup advisor, analyze the current activity and suggest 2-3 proactive actions 
            for a {user_role.value} to consider:

            Recent Activity: {json.dumps(recent_activity, indent=2)}
            AI Team Status: {json.dumps(ai_agents_status, indent=2)}

            Provide suggestions that are:
            1. Timely and relevant to current context
            2. Actionable with clear next steps
            3. Strategic for startup growth
            
            Format as JSON array with: type, message, action, priority"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse and return structured suggestions
            suggestions_text = response.choices[0].message.content
            try:
                return json.loads(suggestions_text)
            except:
                # Fallback if JSON parsing fails
                return [{"type": "general", "message": suggestions_text, "action": "review", "priority": "low"}]
            
        except Exception as e:
            logger.error(f"Error generating proactive suggestions: {e}")
            return []

# Create a singleton instance
openai_service = OpenAIService() 