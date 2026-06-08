import os
import uuid
import json
import time
from collections.abc import AsyncIterable
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()                         

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from graph import agent_builder

# 1. Defining global variables as None initially
pool = None
checkpointer = None
agent = None

# 2. Initializing them INSIDE the lifespan, where the event loop is actively running
@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool, checkpointer, agent
    
    # Safely initialize the pool
    pool = AsyncConnectionPool(os.getenv("DATABASE_URL"), kwargs={"autocommit": True}, open=False)
    await pool.open()
    
    # Now it is safe to create the checkpointer because the event loop exists
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    
    # Compile the agent with the initialized checkpointer
    agent = agent_builder.compile(checkpointer=checkpointer)
    
    yield
    
    # Cleanup on shutdown
    if pool:
        await pool.close()

# 3. Pass the lifespan to FastAPI
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://autonomous-ai-research.vercel.app/"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Total_access_time"]
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    time_taken = time.time() - start_time
    response.headers["Total_access_time"] = str(time_taken)
    return response

class ResearchRequest(BaseModel):
    goal:      str
    depth:     str = "standard"
    thread_id: str = ""

class ResearchResponse(BaseModel):
    status: str
    goal:   str
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Research API!"}

@app.post("/run-agent", response_model=ResearchResponse)
async def run_agent(request: ResearchRequest):
    initial_state = {
        "goal":           request.goal,
        "research_notes": [],
        "attempts":       0,
        "thread_id":      str(uuid.uuid4())
    }
    final_state = await agent.ainvoke(initial_state)
    return ResearchResponse(
        status="success",
        goal=request.goal,
        message=final_state.get("draft_report", "No report generated.")
    )

@app.post("/run-agent-stream")
async def run_agent_stream(request: ResearchRequest):
    async def event_generator():

        thread_id = request.thread_id or str(uuid.uuid4())
        config    = {"configurable": {"thread_id": thread_id}}
        final_state = {}

        yield f"data: {json.dumps({
            'type':      'thread_started',
            'thread_id': thread_id
        })}\n\n"

        async for stream_type, chunk_data in agent.astream(
            {
                "goal":           request.goal,
                "research_notes": [],
                "attempts":       0,
                "thread_id":      thread_id    
            },
            config,
            stream_mode=["updates", "messages"]
        ):
            if stream_type == "updates":
                for node_name, state_update in chunk_data.items():
                    final_state.update(state_update)
                    yield f"data: {json.dumps({
                        'type': 'node_update',
                        'node': node_name
                    })}\n\n"

            elif stream_type == "messages":
                message_chunk, metadata = chunk_data
                speaking_node = metadata.get("langgraph_node", "unknown")
                if speaking_node == "writer" and message_chunk.content:
                    yield f"data: {json.dumps({
                        'type': 'token',
                        'text': message_chunk.content
                    })}\n\n"

        yield f"data: {json.dumps({
            'type':     'done',
            'report':   final_state.get('draft_report', ''),
            'attempts': final_state.get('attempts', 0)
        })}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
