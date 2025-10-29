from fastapi import FastAPI, Depends, HTTPException, Request, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Import GitHub agent functions
from src.agent import get_github_agent, get_execute_custom_task, get_execute_predefined_task
from src.prompts.github_agent_prompt import PREDEFINED_TASKS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get GitHub agent functions using lazy loading - but only store the functions, not the instances
get_agent_fn = get_github_agent
get_execute_custom_task_fn = get_execute_custom_task
get_execute_predefined_task_fn = get_execute_predefined_task

# Create a thread pool for running LLM operations in parallel
# Adjust the max_workers based on your server's capacity
thread_pool = ThreadPoolExecutor(max_workers=10)

# Create FastAPI app
app = FastAPI(
    title="GitHub Agent API",
    description="API for querying the GitHub agent and executing predefined tasks",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Get API token from environment variables
API_TOKEN = os.getenv("API_TOKEN")


# Define request and response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class PredefinedTaskRequest(BaseModel):
    task_key: str
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


# Authentication function (if API_TOKEN is set)
async def verify_token(x_api_token: str = Header(None)):
    if API_TOKEN and (not x_api_token or x_api_token != API_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token",
        )
    return True


# Helper function to format response
def format_response(result):
    """Format the response for better readability."""
    import json

    # If the result is None or empty, return a placeholder
    if not result:
        return {"message": "No results found."}

    # If result is a dict, return it
    if isinstance(result, dict):
        return result

    # If it's a string, analyze and format appropriately
    if isinstance(result, str):
        # Try to parse as JSON if it looks like JSON
        if result.strip().startswith('{') and result.strip().endswith('}'):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass

        # Check if it contains SQL and format it
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE",
                        "CREATE", "ALTER", "DROP", "WITH", "FROM"]
        if any(keyword in result.upper() for keyword in sql_keywords):
            return {"type": "sql", "content": result}

        # Check for lists or tables (lines with delimiter patterns)
        if '|' in result and ('-+-' in result or '+---' in result):
            return {"type": "table", "content": result}

        # Check if it's a list with bullet points
        if result.strip().startswith('- ') or result.strip().startswith('* '):
            return {"type": "list", "content": result}

    # Default return as text
    return {"type": "text", "content": result}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the service is running"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/tasks", dependencies=[Depends(verify_token)] if API_TOKEN else [])
async def list_tasks():
    """Get a list of all predefined tasks available in the GitHub agent"""
    tasks = {}
    for key, description in PREDEFINED_TASKS.items():
        tasks[key] = description

    return {
        "tasks": tasks,
        "count": len(tasks)
    }


@app.post("/query", dependencies=[Depends(verify_token)] if API_TOKEN else [])
async def query(request: QueryRequest):
    """Execute a custom query using the GitHub agent"""
    try:
        start_time = time.time()
        logger.info(
            f"Processing query: {request.query} (session: {request.session_id})")

        if not request.query:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")

        # Get a fresh execute_custom_task function for each request
        execute_custom_task = get_execute_custom_task_fn()

        # Run the agent in a separate thread to avoid blocking the event loop
        # This allows multiple requests to be processed concurrently
        if request.session_id:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: execute_custom_task(request.query, request.session_id)
            )
        else:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: execute_custom_task(request.query)
            )

        if not raw_response:
            return {"message": "No response received from the agent."}

        # Format the response for better readability
        response = format_response(raw_response)

        # Add execution time information
        execution_time = time.time() - start_time
        return {
            "result": response,
            "execution_time": round(execution_time, 2),
            "query": request.query
        }

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/tasks/{task_key}", dependencies=[Depends(verify_token)] if API_TOKEN else [])
async def run_predefined_task(task_key: str, request: PredefinedTaskRequest):
    """Execute a predefined task using the GitHub agent"""
    try:
        start_time = time.time()
        logger.info(
            f"Executing predefined task: {task_key} (session: {request.session_id})")

        if task_key not in PREDEFINED_TASKS:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_key}' not found. Available tasks: {list(PREDEFINED_TASKS.keys())}"
            )

        # Get a fresh execute_predefined_task function for each request
        execute_predefined_task = get_execute_predefined_task_fn()

        # Execute the predefined task in a separate thread
        if request.session_id:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: execute_predefined_task(task_key, request.session_id)
            )
        else:
            raw_response = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: execute_predefined_task(task_key)
            )

        if not raw_response:
            return {"message": "No response received from the agent."}

        # Format the response for better readability
        response = format_response(raw_response)

        # Add execution time information
        execution_time = time.time() - start_time
        return {
            "result": response,
            "execution_time": round(execution_time, 2),
            "task": task_key,
            "task_description": PREDEFINED_TASKS[task_key]
        }

    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing task: {str(e)}")


# Request logger middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - Completed in {process_time:.2f}s - Status: {response.status_code}")
    return response


if __name__ == "__main__":
    # This block won't be executed when running with Uvicorn
    import uvicorn
    uvicorn.run("github_agent_server:app",
                host="0.0.0.0", port=8005, reload=True)
