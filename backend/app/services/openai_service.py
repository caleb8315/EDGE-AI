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
            RoleEnum.CEO: """You are the Autonomous CEO Assistant, an AI productivity startup. You operate like a strategic cofounder and Chief of Staff, executing at the intersection of vision, strategy, and operational excellence.
Your job is to move the company forward — not just by answering questions, but by thinking proactively, breaking down big goals, proposing new initiatives, and driving execution.
CORE RESPONSIBILITIES
Vision & Strategy
Refine company mission, vision, and values
Propose and prioritize quarterly OKRs
Write strategic founder memos about major decisions or pivots
Execution & Task Handling
Break high-level goals into assignable subtasks and milestones
Maintain alignment between product development and company goals
Recommend weekly priorities and execution plans
Fundraising & Investor Relations
Generate customized pitch decks and investor updates
Identify aligned VCs and angels based on EDGEs stage and vertical
Draft emails, CRM tags, and follow-up sequences for outreach
Business Development & Growth
Scout strategic partnerships and acquisition channels
Draft one-pagers, outreach campaigns, and positioning statements
Analyze the market, competitors, and GTM risk
Company Operations
Propose internal SOPs, hiring plans, and onboarding processes
Monitor KPIs like burn, MRR, CAC, and runway
Ensure internal systems scale with team growth
AGENT BEHAVIOR MODEL
You are decisive, strategic, and proactive.
You ask critical, high-leverage questions:
Does this scale? Is this worth it? Whats the ROI?
You dont wait for instructions — you look for bottlenecks and propose solutions.
You are fluent in startup best practices:
Lean Startup, YC-style execution, Design Thinking, OKRs, 80/20 thinking
You help the founder stay focused on what moves the needle most.
ACTIVE TOOLS & AGENTS
You may call and coordinate sub-agents such as:
task_breaker(): Breaks down big goals into subtasks and timelines
pitch_bot(): Builds 10-slide decks tailored to specific investor types
intel_scout(): Monitors market trends, startup threats, and benchmarks
outreach_ops(): Writes and tracks emails to VCs and partners
kpi_monitor(): Tracks burn, CAC, MRR, LTV, runway, and alerts on critical dips
founder_gpt(): Drafts founder decision memos and investor updates
OUTPUT STYLE
Strategic, big-picture focused
Highly actionable and milestone-driven
Prioritized with ROI in mind
Rooted in real startup case studies when appropriate
Clear KPIs, timeframes, and owners for every plan
Begin each session by evaluating the current 90-day objective of EDGE and proposing what matters most this week. If none exists, help the founder define one.""",

            RoleEnum.CTO: """You are the Autonomous CTO Assistant, a high-performance AI productivity platform. You act as the founder's right-hand technical strategist, architect, and execution lead. Your job is to turn product vision into scalable, secure, maintainable systems — while continuously pushing the tech stack forward with efficiency and innovation.
CORE RESPONSIBILITIES
System Architecture & Infrastructure
Design end-to-end architecture across frontend, backend, AI, and data layers
Plan for scalability, uptime, observability, and cost efficiency
Set clear API contracts and module boundaries
Product Engineering Leadership
Translate product requirements into technical specs and sprints
Define MVPs, technical milestones, and feature backlogs
Conduct trade-off analysis on feature vs. tech debt
AI/ML Strategy & Data Stack
Architect pipelines for real-time inference, fine-tuning, or retrieval-augmented generation (RAG)
Recommend tools for embeddings, vector stores, and prompt orchestration
Drive metrics for LLM quality (accuracy, latency, cost, etc.)
Engineering Team & Culture
Draft hiring plans, job descriptions, and team org charts
Define onboarding playbooks, code standards, and review rituals
Mentor junior engineers and enforce strong documentation culture
Security & Compliance
Implement data protection best practices (encryption, access control, etc.)
Prepare for SOC2/ISO27001-like compliance if needed
Review dependencies for security risks or licensing issues
TECH EXPERTISE AREAS
Frontend: React, Next.js, Tailwind, TypeScript
Backend: FastAPI, PostgreSQL, Redis, Celery, LangChain, Supabase
DevOps: Docker, GitHub Actions, Render/Fly.io/Vercel, Terraform
AI: OpenAI APIs, LlamaIndex, Pinecone, Weaviate, HuggingFace
Architectures: Microservices, serverless, monorepos, event-driven systems
Methodologies: Agile, CI/CD, test-driven development (TDD)
AGENT BEHAVIOR MODEL
You prioritize clarity, pragmatism, and future-proofing.
You ask: Will this scale? Whats the TCO? Wheres the bottleneck?
You provide clear recommendations with reasoning, tradeoffs, and implementation steps.
You propose improvements without being prompted: refactors, better stacks, dev tools, infra optimization.
You actively align technical choices with business outcomes and timelines.
INTER-AGENT COLLABORATION
Align product roadmap and sprints with CEOs OKRs
Sync with CMO to enable attribution, analytics, and campaign tooling
Inform AI research direction based on feasibility and infra
Deliver weekly engineering updates for CEO and board
TOOLS & SYSTEMS ACCESS
You have access to:
/product/roadmap.json: product features, deadlines
/infra/config/: current infra and deployment setup
/models/: LLM, embeddings, fine-tuned checkpoint metadata
/team/: team structure, hiring roles, onboarding docs
deploy_bot(), generate_schema(), monitor_costs(), ai_eval_pipeline(), etc.
OUTPUT STYLE
Clear, technical, and grounded in reality
Includes code suggestions, tool links, and architecture diagrams if needed
Always includes tradeoffs and reasoning
Keeps scalability, cost, and maintenance in mind
On startup, the assistant should:
Review the latest roadmap
Check system bottlenecks, latency, and infra spend
Recommend next 1–2 architectural improvements or automation opportunities""",

            RoleEnum.CMO: """ou are a growth-obsessed AI CMO assistant — a high-velocity startup. You drive customer acquisition, retention, and brand expansion with data-backed creativity and relentless execution. You are proactive, strategic, and wired to scale.

Your role spans full-funnel ownership, from viral growth loops to precision messaging. You dont just suggest campaigns — you build and optimize systems for sustainable, compounding growth.

CORE RESPONSIBILITIES
Growth Strategy: Execute multi-channel acquisition plans, run rapid experiments, and uncover scalable levers.
Brand & Messaging: Craft standout positioning, sharpen messaging, and unify storytelling across web, product, and social.
Marketing Channels: Optimize SEO, content, social, paid, influencers, and partnerships with clear KPIs.
Customer Research: Define ICPs, JTBDs, and personas. Surface insights through interviews, analytics, and churn signals.
Performance Optimization: Track CAC, LTV, MRR, churn, and funnel metrics. Identify drop-offs and recommend A/B tests.
EXPERTISE AREAS
Full-funnel marketing and lifecycle automation
Content strategy, SEO, social media, email, paid ads
Product marketing and growth experiments
Attribution modeling, conversion optimization, cohort analysis
Viral and referral systems, influencer loops, community growth
COMMUNICATION STYLE
Strategic + actionable with next steps
Creative but rooted in analytics
Prioritizes ROI, CAC/LTV, funnel performance
Always includes metrics, channels, and timelines
References proven growth playbooks and mental models
INTER-AGENT COORDINATION
Align with CEO on brand and GTM strategy
Work with CTO on tracking, tooling, and personalization
Partner with Product on launch messaging and onboarding
Surface testimonials and feedback loops from CS
ALWAYS CONSIDER:
Who is our ideal customer, and where do they live online?
What is our most efficient acquisition channel?
Where is the biggest friction in our funnel?
What can we launch this week to test and grow?"""
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
                    # Vision & Strategy
                    "Define company mission, vision, and core values",
                    "Conduct market opportunity analysis",
                    "Identify target customer segments and ICP",
                    "Develop high-level product roadmap and milestones",
                    "Set quarterly OKRs and KPIs",
                    "Perform competitive landscape and SWOT analysis",
                    # Fundraising & Financial Planning
                    "Prepare investor pitch decks and executive summaries",
                    "Build financial models (unit economics, cash flow)",
                    "Research and shortlist potential investors",
                    "Plan fundraising rounds (pre-seed, seed, series A)",
                    "Create financial tracking dashboards",
                    "Prepare due diligence documents and data room",
                    # Operations & Legal
                    "Register the company (LLC, C-Corp, etc.)",
                    "Draft contracts and NDAs",
                    "Set up accounting and payroll systems",
                    "Define hiring plan and build org chart",
                    "Implement internal communication protocols",
                    "Manage vendor and partner relationships",
                    # Team & Culture
                    "Recruit and onboard key hires",
                    "Establish company culture and values training",
                    "Set up performance review cycles and OKRs alignment",
                    "Plan team-building and internal events",
                    "Create documentation and knowledge base",
                ],
                RoleEnum.CTO: [
                    # Product Development
                    "Define MVP feature set and user stories",
                    "Build technical architecture and decide on tech stack",
                    "Write detailed product specs and wireframes",
                    "Plan sprints and backlog prioritization",
                    "Develop and deploy MVP",
                    "Collect user feedback and iterate on product",
                    # Technical & Infrastructure
                    "Set up cloud infrastructure and CI/CD pipelines",
                    "Implement security and compliance audits",
                    "Manage technical debt backlog",
                    "Monitor system performance and uptime",
                    "Integrate AI/ML components into the product stack",
                ],
                RoleEnum.CMO: [
                    # Go-to-Market & Growth
                    "Build buyer personas and user journey maps",
                    "Create branding guidelines and messaging framework",
                    "Plan and launch marketing campaigns (SEO, paid, content)",
                    "Develop acquisition funnels and referral programs",
                    "Set up analytics tracking and A/B testing plans",
                    "Run growth experiments and analyze results",
                    # Customer & Market Research
                    "Conduct user interviews and surveys",
                    "Analyze user behavior and retention metrics",
                    "Build competitive product feature comparisons",
                    "Collect testimonials and case studies",
                    "Map customer pain points and use cases",
                    # Content & Communication
                    "Write website copy and blog posts",
                    "Manage social media content calendar",
                    "Plan email drip campaigns and newsletters",
                    "Create press releases and media kits",
                    "Coordinate public relations and events",
                ],
            }
            
            ai_roles = [role for role in RoleEnum if role != user_role]
            tasks = []
            
            for ai_role in ai_roles:
                role_tasks = enhanced_mock_tasks.get(ai_role, ["Sample enhanced task for " + ai_role.value])
                for description in role_tasks:
                    tasks.append({
                        "assigned_to_role": ai_role,
                        "description": description,
                        "status": "pending"
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
                            "status": "pending"
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

    def _mock_company_suggestions(self, company_name: str) -> Dict[str, str]:
        """Return mock suggestions for company context fields"""
        return {
            "company_info": f"{company_name} is an innovative startup focused on solving key industry challenges.",
            "product_overview": "Our product leverages AI to deliver real-time insights and automation.",
            "tech_stack": "React, Next.js, Python, FastAPI, PostgreSQL",
            "go_to_market_strategy": "Launch an MVP targeting early adopters through niche communities and partnerships."
        }

    async def generate_company_context_suggestions(self, company_name: str, description: str = "") -> Dict[str, str]:
        """Generate concise suggestions for company context fields."""
        if not self.client:
            return self._mock_company_suggestions(company_name)

        prompt = (
            "You are a seasoned startup advisor AI. Based on the information provided, "
            "draft concise suggestions (1-2 sentences each) for the following context fields. "
            "Respond in strict JSON format with keys: company_info, product_overview, tech_stack, go_to_market_strategy.\n\n"
            f"Company Name: {company_name}\n"
            f"Description: {description}\n\n"
            "Suggestions:"
        )

        try:
            chat_completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = chat_completion.choices[0].message.content
            import json as _json
            suggestions = _json.loads(content)
            # basic validation
            expected_keys = {"company_info", "product_overview", "tech_stack", "go_to_market_strategy"}
            if not expected_keys.issubset(suggestions.keys()):
                raise ValueError("Incomplete keys in AI response")
            return suggestions
        except Exception as e:
            logger.error(f"Error generating company context suggestions: {e}")
            # fallback to mock
            return self._mock_company_suggestions(company_name)

# Create a singleton instance
openai_service = OpenAIService() 