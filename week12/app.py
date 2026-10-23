from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from agent import run as run_agent

app = FastAPI(title="Smart Website Monitoring Agent API")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    blocked_docs: list
    latency: float
    status: str

MAX_QUERY_LENGTH = 500
TIMEOUT_SECONDS = 300

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "agent-api"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if len(request.query) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail="Query exceeds budget limit (max 500 chars).")
    
    start_time = time.time()
    
    try:
        answer, blocked = await asyncio.wait_for(
            asyncio.to_thread(run_agent, request.query),
            timeout=TIMEOUT_SECONDS
        )
        
        latency = time.time() - start_time
        return ChatResponse(
            answer=answer, 
            blocked_docs=blocked, 
            latency=round(latency, 2), 
            status="success"
        )
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Agent request timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))