from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Total_access_time"]
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    time_taken = time.time() - start_time
    print(f"Time taken for the request: {time_taken:.4f} seconds")
    response.headers["Total_access_time"] = str(time_taken)
    return response

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