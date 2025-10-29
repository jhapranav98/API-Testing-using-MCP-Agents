#!/usr/bin/env python3
"""
FastAPI Server for JIRA Agent
"""

from concurrent.futures import ThreadPoolExecutor
import asyncio
import time
from src.agent.jira_agent import create_jira_agent
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JIRA Agent Server",
    description="FastAPI server for JIRA Agent with MCP tools integration",
    version="1.0.0"
)

# Initialize single agent
jira_agent = None


# Match Snowflake agent's request model
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global jira_agent
    try:
        logger.info("Initializing JIRA Agent...")
        jira_agent = create_jira_agent()
        logger.info("JIRA Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "jira-agent"}


# Match Snowflake agent's /query endpoint and response style

# Thread pool for sync agent calls (if needed)
thread_pool = ThreadPoolExecutor(max_workers=10)


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """Main query endpoint for JIRA agent (Snowflake style)"""
    try:
        if jira_agent is None:
            raise HTTPException(
                status_code=500, detail="Agent not initialized")

        start_time = time.time()
        logger.info(
            f"Processing JIRA query: {request.query} (session: {request.session_id})")

        # Run the agent in a thread pool for concurrency (sync calls only)
        if request.session_id:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: jira_agent.chat(request.query, request.session_id)
            )
        else:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: jira_agent.chat(request.query)
            )

        if not raw_response:
            return {"result": "No response received from the agent."}

        execution_time = time.time() - start_time
        return {
            "result": raw_response,
            "execution_time": round(execution_time, 2),
            "session_id": request.session_id
        }

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List available agent and status"""
    return {
        "agent": {
            "jira": {"status": "active" if jira_agent else "inactive"}
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "jira_agent_server:app",
        host="0.0.0.0",
        port=8002,
        log_level="info",
        timeout_keep_alive=600,  # 10 minutes keep-alive
        timeout_graceful_shutdown=60
    )



