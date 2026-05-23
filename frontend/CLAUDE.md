@AGENTS.md
# 🤖 50-Day AI Engineer Roadmap
### Autonomous AI Research Department — Full Project Blueprint

> **Stack:** Python + LangGraph + FastAPI (backend) · Next.js + Tailwind (frontend) · PostgreSQL (memory)  
> **Goal:** Build a multi-agent research system where AI agents orchestrate, research, write, and critique each other in real-time.

---

## 🧠 What You're Building

A multi-agent AI system with 4 specialized agents:

| Agent | Job |
|---|---|
| **Orchestrator** | Reads the goal and plans the steps |
| **Researcher** | Uses Tavily web search to find live data |
| **Writer** | Synthesizes research into a structured report |
| **Critic** | Evaluates the draft — rejects or approves it |

If the Critic rejects → loops back to Researcher → retries → Critic approves → final output streamed to Next.js dashboard in real-time.

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI Orchestration | LangGraph + LangChain | Agent graph, loops, conditional edges |
| AI Models | Anthropic Claude API | Powers each agent node |
| Web Search | Tavily API | Gives Researcher live internet access |
| Backend | FastAPI + Python | Exposes agents as API endpoints |
| Frontend | Next.js + Tailwind CSS | Real-time dashboard |
| Database | PostgreSQL (Docker) | Agent memory + checkpointing |
| Deployment | Railway (API) + Vercel (UI) | Production hosting |

---

## 🗓️ Phase 1 — Python Fast-Track & API Setup (Days 1–10)

> **Goal:** Learn Python fast, get FastAPI running, connect it to Next.js

| Day | Task | Tag |
|---|---|---|
| 1 | Python syntax crash course — variables, functions, loops, types | `Python` |
| 2 | Classes, list comprehensions, f-strings, pip & venv setup | `Python` |
| 3 | Async/await in Python — compare with JS async patterns | `Python` |
| 4 | Pydantic models — how Python handles typed data (like TS interfaces) | `Python` |
| 5 | Build your first FastAPI server with a GET + POST route | `FastAPI` |
| 6 | Connect Next.js to FastAPI — hit the endpoint from the browser | `FastAPI` |
| 7 | Add request validation and error handling to FastAPI | `FastAPI` |
| 8 | Learn Python decorators & middleware (FastAPI uses them everywhere) | `Python` |
| 9 | Set up CORS, .env variables, and project folder structure | `Setup` |
| 10 | Mini project: FastAPI endpoint that accepts a query and returns structured mock agent JSON | `Project` |

### Phase 1 Setup Commands
```bash
# Create project
mkdir ai-research-agent && cd ai-research-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv

# Save dependencies
pip freeze > requirements.txt

# Run server
cd backend
uvicorn main:app --reload
```

### Phase 1 Folder Structure
```
ai-research-agent/
├── venv/
├── backend/
│   ├── main.py
│   └── .env
├── frontend/          ← Next.js goes here (Day 6)
└── requirements.txt
```

---

## 🗓️ Phase 2 — Building the Agent Graph (Days 11–25)

> **Goal:** Build real LangGraph nodes, connect them, add Claude AI to each node

| Day | Task | Tag |
|---|---|---|
| 11 | Install LangGraph + LangChain, understand the graph mental model | `LangGraph` |
| 12 | Define your AgentState with Pydantic — the data that flows between nodes | `LangGraph` |
| 13 | Write your first node function (Orchestrator) that reads the goal | `LangGraph` |
| 14 | Write the Researcher node — takes goal, returns raw notes (mocked) | `LangGraph` |
| 15 | Write the Writer node — takes notes, returns a draft report | `LangGraph` |
| 16 | Connect all 3 nodes linearly in a LangGraph StateGraph | `LangGraph` |
| 17 | Run your first end-to-end graph with a test input | `LangGraph` |
| 18 | Add Claude (via Anthropic API) to the Orchestrator node | `AI` |
| 19 | Add Claude to the Writer node — real LLM synthesis | `AI` |
| 20 | Add streaming output from LangGraph via FastAPI | `FastAPI` |
| 21 | Expose the graph run as a POST /run-agent endpoint | `FastAPI` |
| 22 | Test the API with Postman — verify state flows correctly | `Testing` |
| 23 | Error handling — what if a node fails? Add retries | `Testing` |
| 24 | Add logging — print which node is running and what state it holds | `Dev` |
| 25 | ✅ Milestone: 3-node graph running end-to-end with real AI responses | `Milestone` |

### Phase 2 Install Commands
```bash
pip install langgraph langchain langchain-anthropic
pip freeze > requirements.txt
```

### AgentState Structure (Day 12)
```python
from pydantic import BaseModel

class AgentState(BaseModel):
    goal: str
    research_notes: list[str] = []
    draft_report: str = ""
    critic_feedback: str = ""
    attempts: int = 0
    status: str = "pending"
```

---

## 🗓️ Phase 3 — Loops, Tools & Memory (Days 26–40)

> **Goal:** Add web search, build the Critic loop, add PostgreSQL checkpointing

| Day | Task | Tag |
|---|---|---|
| 26 | Set up Tavily API account and test a raw search query | `Tools` |
| 27 | Give the Researcher node a real web search tool via LangChain | `Tools` |
| 28 | Test Researcher with live data — verify results are usable | `Tools` |
| 29 | Write the Critic node — evaluates the Writer draft against criteria | `LangGraph` |
| 30 | Build the conditional edge — Critic returns "approve" or "reject" | `LangGraph` |
| 31 | Wire the reject path back to Researcher — the loop is alive | `LangGraph` |
| 32 | Add max retry guard — stop the loop after 3 rejections | `LangGraph` |
| 33 | Test full loop: goal → research → write → critique → loop back → approve | `Testing` |
| 34 | Set up PostgreSQL locally with Docker | `Database` |
| 35 | Integrate LangGraph checkpointing with PostgreSQL | `Database` |
| 36 | Test that a failed run can resume from the last checkpoint | `Database` |
| 37 | Add thread_id support — each user request is its own session | `Database` |
| 38 | Stress test with 3 different research goals — fix any failures | `Testing` |
| 39 | Optimize prompts in Critic node — too strict = infinite loops | `AI` |
| 40 | ✅ Milestone: Full agentic loop with memory, tools, and live search | `Milestone` |

### Phase 3 Install Commands
```bash
# Tavily search
pip install tavily-python

# PostgreSQL driver
pip install psycopg2-binary

# Docker — PostgreSQL (run this once on Day 34)
docker run --name agent-db \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=agentdb \
  -p 5432:5432 \
  -d postgres

pip freeze > requirements.txt
```

### .env File Setup
```env
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:secret@localhost:5432/agentdb
```

### Critic Conditional Logic (Day 30)
```python
def should_continue(state: AgentState) -> str:
    if state.attempts >= 3:
        return "end"          # max retries hit — force finish
    if state.status == "approved":
        return "end"          # critic approved — we're done
    return "researcher"       # critic rejected — loop back
```

---

## 🗓️ Phase 4 — Next.js Dashboard & Polish (Days 41–50)

> **Goal:** Build the real-time dashboard, stream agent output live, deploy everything

| Day | Task | Tag |
|---|---|---|
| 41 | Boot Next.js App Router project, set up Tailwind, basic layout | `Next.js` |
| 42 | Build the goal input form — textarea + submit button | `Next.js` |
| 43 | Connect form to FastAPI — POST the goal, get response | `Next.js` |
| 44 | Implement Server-Sent Events (SSE) in FastAPI for streaming | `Streaming` |
| 45 | Consume SSE stream in Next.js — show live agent updates | `Streaming` |
| 46 | Build the agent activity feed UI — show each node as it runs | `Next.js` |
| 47 | Build the final report display — render markdown output | `Next.js` |
| 48 | Add loading states, error states, and retry UI | `Next.js` |
| 49 | Deploy FastAPI to Railway, Next.js to Vercel | `Deploy` |
| 50 | Write README, record 2-min demo video for portfolio | `Portfolio` |

### Phase 4 Install Commands
```bash
# Frontend
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install react-markdown

# Backend SSE dependency
pip install sse-starlette
pip freeze > requirements.txt
```

### SSE Streaming Setup (Day 44)
```python
from sse_starlette.sse import EventSourceResponse

@app.post("/run-agent-stream")
async def run_agent_stream(request: ResearchRequest):
    async def event_generator():
        yield {"data": '{"agent": "orchestrator", "status": "running"}'}
        yield {"data": '{"agent": "researcher", "status": "running"}'}
        yield {"data": '{"agent": "writer", "status": "running"}'}
        yield {"data": '{"agent": "critic", "status": "approved"}'}
    return EventSourceResponse(event_generator())
```

---

## ⚠️ Critical Warnings

| Risk | Solution |
|---|---|
| Critic too strict → infinite loop | Add max 3 retry guard on Day 32 **before** testing |
| Deploy surprises | Deploy a basic version on Day 43, not Day 49 |
| venv not activated | Always check for `(venv)` in terminal |
| CORS errors | Add CORSMiddleware to FastAPI before connecting Next.js |
| Docker on Day 34 | Install Docker today, use it on Day 34 |

---

## 📚 APIs & Accounts You Need

| Service | Purpose | When | Cost |
|---|---|---|---|
| Anthropic API | Powers all AI agents | Day 18 | Pay per token |
| Tavily API | Web search for Researcher | Day 26 | ~$5-10/month dev |
| Railway | Deploy FastAPI | Day 49 | Free tier available |
| Vercel | Deploy Next.js | Day 49 | Free tier available |

---

## 🎯 Portfolio Story After Day 50

> *"I built a multi-agent AI research system. The orchestration layer runs in Python with LangGraph — agents plan, research with live web search, write reports, and critique each other in a loop. The backend is FastAPI with PostgreSQL checkpointing so no work is lost on long tasks. The frontend is Next.js with real-time streaming so users watch agents think live."*

**Projects combined:**

| Project | What it proves |
|---|---|
| RAG DSA Chatbot | Memory, retrieval, embeddings |
| This Agent System | Autonomy, loops, orchestration |
| Next.js frontend | Can ship a real product |

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd ai-research-agent

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # add your API keys
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

*Built in 50 days. From zero Python to full AI Engineer portfolio.* 🔥