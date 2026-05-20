from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    goal: str
    depth: str = "standard"

class ResearchResponse(BaseModel):
    status: str
    goal: str
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Research API!"}

@app.post("/run-agent", response_model=ResearchResponse)
async def run_agent(request: ResearchRequest):
    return ResearchResponse(
        status="received",
        goal=request.goal,
        message=f"Processing your research goal: {request.goal}"
    )