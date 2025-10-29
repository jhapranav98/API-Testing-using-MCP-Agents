from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.agent.supervisor_agent import execute_supervisor_agent_with_retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread pool for running synchronous operations
thread_pool = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
    title="Supervisor Agent API",
    description="API for routing tasks to Jira and Test Case Creation agents via the Supervisor Agent",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    result: str
    execution_time: float
    session_id: str


@app.post("/query", response_model=QueryResponse)
async def supervisor_task(request: QueryRequest):
    start_time = time.time()
    logger.info(f"[API] Received query: {request.query[:100]}... (session: {request.session_id})")
    
    try:
        # Log progress
        logger.info(f"[API] Starting supervisor agent execution...")
        
        # Run the supervisor agent in a thread pool to avoid blocking
        result = await asyncio.get_event_loop().run_in_executor(
            thread_pool,
            lambda: asyncio.run(execute_supervisor_agent_with_retry(request.query, request.session_id))
        )
        
        execution_time = time.time() - start_time
        logger.info(f"[API] Task completed in {execution_time:.2f} seconds")
        
        return QueryResponse(
            result=result,
            execution_time=round(execution_time, 2),
            session_id=request.session_id
        )
    except asyncio.TimeoutError:
        execution_time = time.time() - start_time
        logger.error(f"[API] Task timed out after {execution_time:.2f} seconds")
        raise HTTPException(
            status_code=504, detail=f"Task timed out after {execution_time:.2f} seconds"
        )
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[API] Error after {execution_time:.2f} seconds: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing task: {str(e)}")


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("supervisor_agent_server:app",
                host="0.0.0.0", port=8004, reload=True,
                timeout_keep_alive=600,  # 10 minutes keep-alive
                timeout_graceful_shutdown=60)
