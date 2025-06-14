🧠 EDGE — Your AI Startup Team

EDGE is a collaborative, AI-powered startup assistant that helps founders launch, plan, and scale their companies faster than ever. Pick your role (CEO, CTO, or CMO), and let autonomous AI agents take on the rest — brainstorming, building, marketing, and executing ideas alongside you.

⚡️ Think of EDGE as your always-on, ultra-smart cofounding team.
🧩 Platform Overview

This monorepo includes:

Service	Tech Stack	Description
backend/	Python, FastAPI, OpenAI, Supabase	Handles AI orchestration, task management, and data logic
frontend/	Next.js 14, TypeScript, TailwindCSS, Supabase JS	Modern SPA for onboarding, messaging, and interactions
✨ Key Features

🔐 Supabase Auth with JWTs
🤖 OpenAI GPT-powered autonomous agents (CEO / CTO / CMO)
🧠 Per-agent memory + task state stored in Supabase
🔄 Real-time updates between agents and user
⚡️ FastAPI + RESTful backend with Swagger docs
💻 Next.js 14 frontend with Tailwind and TypeScript
🚀 Deploy-ready for Vercel, Fly.io, or Docker
📱 Mobile-friendly, responsive design
📁 Project Structure

EDGE/
├── backend/            # FastAPI + OpenAI + Supabase
│   ├── app/            # FastAPI app source
│   ├── requirements.txt
│   └── ...
├── frontend/           # Next.js 14 SPA
│   ├── src/            # Frontend source code
│   └── ...
├── README.md
└── .env.example        # Environment variable template
🧪 Database Schema (Supabase)

users
Field	Type	Description
id	UUID	Primary key
email	text	User’s email
role	text	CEO, CTO, or CMO
created_at	timestamp	Auto-generated
agents
Field	Type	Description
id	UUID	Primary key
user_id	UUID	Foreign key to users
role	text	Agent role (CEO, CTO, or CMO)
conversation_state	JSONB	Stored chat context for OpenAI
created_at	timestamp	Auto-generated
tasks
Field	Type	Description
id	UUID	Primary key
user_id	UUID	Foreign key to users
assigned_to_role	text	CEO, CTO, or CMO
description	text	Task summary
status	text	pending, in_progress, or completed
created_at	timestamp	Auto-generated
⚙️ Environment Setup

🔑 .env Configuration
Copy the example file and add your API credentials:

cp backend/.env.example backend/.env
Example:

SUPABASE_URL="https://<your-project>.supabase.co"
SUPABASE_KEY="<service_role_or_anon_key>"
OPENAI_API_KEY="sk-..."
ENVIRONMENT="development"
🚀 Getting Started

1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/edge.git
cd edge
2. Backend – FastAPI
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
3. Frontend – Next.js 14
Open a new terminal:

cd frontend
npm install
npm run dev
# Web: http://localhost:3000
🧪 Tests

Backend:

python backend/test_api.py
Frontend:

npm run lint     # ESLint
npm run test     # Jest (optional)
🛠 Requirements

Python 3.10+
Node.js 18+ + npm or yarn
Supabase account
OpenAI API key
(Optional) Docker Desktop for containerization
🧠 Example Use Case

Sarah signs up as the CTO. EDGE automatically assigns an AI CEO and CMO.
She chats with her AI CEO about product-market fit and gets marketing ideas from the AI CMO — while EDGE tracks tasks, strategies, and progress across the entire startup lifecycle.
🤝 Contributing

Fork → git checkout -b feature/my-feature
Commit → git commit -m 'feat: add something'
Push → git push origin feature/my-feature
Open a PR — we love clean, well-documented code!


RUN BACKEND:
python -m uvicorn app.main:app --reload --port 8000 --log-level debug
