from collections.abc import AsyncIterable
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import json
from graph import agent_builder

app = FastAPI()

# Compile once at startup ✅
agent = agent_builder.compile()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Total_access_time"]
)

# Timing middleware ✅
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    time_taken = time.time() - start_time
    print(f"Time taken: {time_taken:.4f} seconds")
    response.headers["Total_access_time"] = str(time_taken)
    return response

# Models
class ResearchRequest(BaseModel):
    goal: str
    depth: str = "standard"

class ResearchResponse(BaseModel):
    status: str
    goal: str
    message: str

# Route 1 — Health check
@app.get("/")
async def root():
    return {"message": "Welcome to the Research API!"}

# Route 2 — Simple sync (testing/Postman)

@app.post("/run-agent", response_model=ResearchResponse)
async def run_agent(request: ResearchRequest):
    initial_state = {
        "goal":           request.goal,
        "research_notes": [],
        "attempts":       0
    }
    # await + ainvoke for async ✅
    final_state = await agent.ainvoke(initial_state)
    
    return ResearchResponse(
        status="success",
        goal=request.goal,
        message=final_state.get("draft_report", "No report generated.")
    )

# Route 3 — Streaming (main UI demo)
@app.post("/run-agent-stream")
async def run_agent_stream(request: ResearchRequest):
    async def event_generator():
        final_state = {}

        async for stream_type, chunk_data in agent.astream(
            {
                "goal": request.goal,
                "research_notes": [],
                "attempts": 0
            },
            stream_mode=["updates", "messages"] 
        ):
            # 2. Handle the "updates" (Node transitions) exactly as before
            if stream_type == "updates":
                for node_name, state_update in chunk_data.items():
                    final_state.update(state_update)
                    yield f"data: {json.dumps({'type': 'node_update', 'node': node_name})}\n\n"

            # 3. Handle the "messages" (The Typewriter Tokens)
            elif stream_type == "messages":
                # LangGraph message chunks are returned as a tuple: (MessageChunk, Metadata)
                message_chunk, metadata = chunk_data
                
                # Figure out who is currently speaking
                speaking_node = metadata.get("langgraph_node", "unknown")
                
                # THE FILTER: Only send tokens to Next.js IF it is the Writer node!
                if speaking_node == "writer":
                    if message_chunk.content:
                        yield f"data: {json.dumps({
                            'type': 'token', 
                            'text': message_chunk.content
                        })}\n\n"

        # Send final report once
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