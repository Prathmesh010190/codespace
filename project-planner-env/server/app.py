import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path so we can import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    PlannerAction,
    PlannerObservation,
    PlannerState,
    StepResult,
    GraderResult,
)
from server.environment import ProjectPlannerEnvironment


# ══════════════════════════════════════════════════════
#  APP SETUP
# ══════════════════════════════════════════════════════

# Global environment instance
env: Optional[ProjectPlannerEnvironment] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize environment when server starts."""
    global env
    print("🚀 Starting ProjectPlannerEnv server...")
    env = ProjectPlannerEnvironment()
    print("✅ Environment loaded successfully!")
    print(f"   📋 Projects: {len(env._projects)}")
    print(f"   👥 Teams: {len(env._teams)}")
    print(f"   📊 Ground truth: {len(env._ground_truth)} projects")
    yield
    print("👋 Shutting down ProjectPlannerEnv server...")


app = FastAPI(
    title="ProjectPlannerEnv",
    description=(
        "An OpenEnv environment where AI agents act as Project Managers. "
        "Agents receive project briefs and create sprint plans, which are "
        "graded on task coverage, skill-assignment match, availability "
        "compliance, dependency correctness, and risk identification."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════
#  REQUEST/RESPONSE MODELS
# ══════════════════════════════════════════════════════

class ResetRequest(BaseModel):
    """Request body for /reset endpoint."""
    task_type: str = "easy"
    project_id: Optional[str] = None


class StepRequest(BaseModel):
    """Request body for /step endpoint."""
    action: PlannerAction


class GraderRequest(BaseModel):
    """Request body for /grader endpoint."""
    task_type: str = "easy"
    project_id: str = "proj_001"
    action: PlannerAction


class HealthResponse(BaseModel):
    """Response for /health endpoint."""
    status: str = "healthy"
    environment: str = "ProjectPlannerEnv"
    version: str = "1.0.0"


# ══════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns 200 if the server is running.
    Required for HF Space deployment validation.
    """
    return HealthResponse()


@app.post("/reset", response_model=StepResult)
async def reset(request: ResetRequest):
    """
    Start a new episode.
    
    Args:
        task_type: "easy", "medium", or "hard"
        project_id: Optional specific project ID
    
    Returns:
        StepResult with initial observation
    """
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    try:
        result = env.reset(
            task_type=request.task_type,
            project_id=request.project_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step", response_model=StepResult)
async def step(request: StepRequest):
    """
    Submit an action (project plan) and get graded.
    
    Args:
        action: PlannerAction with tasks, risks, sprint_summary
    
    Returns:
        StepResult with reward, feedback, and grading breakdown
    """
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    try:
        result = env.step(request.action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state", response_model=PlannerState)
async def get_state():
    """
    Get current episode metadata.
    
    Returns:
        PlannerState with episode_id, step_count, task type, etc.
    """
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    return env.state()


@app.get("/tasks")
async def get_tasks():
    """
    List all available tasks with descriptions and scoring criteria.
    
    Returns:
        List of task definitions with required fields and scoring info.
    """
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    return {
        "tasks": env.get_available_tasks(),
        "action_schema": {
            "tasks": {
                "type": "list",
                "items": {
                    "name": "string (required)",
                    "assignee": "string (required for medium/hard)",
                    "estimated_days": "float (required for medium/hard)",
                    "priority": "integer (required for hard)",
                    "depends_on": "list[string] (required for hard)",
                    "category": "string: backend/frontend/testing/design/devops",
                }
            },
            "risks": "list[string] (required for hard)",
            "sprint_summary": "string (required for hard)",
        }
    }


@app.post("/grader")
async def run_grader(request: GraderRequest):
    """
    Run grader independently on a plan.
    
    Useful for testing grading logic without running a full episode.
    
    Args:
        task_type: Difficulty level
        project_id: Which project to grade against
        action: The plan to grade
    
    Returns:
        GraderResult with score, breakdown, and feedback
    """
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    try:
        # Reset to the specified project (sets up ground truth)
        env.reset(task_type=request.task_type, project_id=request.project_id)
        # Grade the action
        result = env.step(request.action)
        return {
            "score": result.reward,
            "breakdown": result.info.get("grader_breakdown", {}),
            "feedback": result.info.get("grader_feedback", ""),
            "penalties": result.info.get("penalties", []),
            "bonuses": result.info.get("bonuses", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading failed: {str(e)}")


@app.post("/baseline")
async def run_baseline():
    """
    Run baseline inference using OpenAI API.
    Triggers the baseline script and returns scores for all 3 tasks.
    
    Requires OPENAI_API_KEY environment variable.
    
    Returns:
        Baseline scores for easy, medium, and hard tasks.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY environment variable not set. "
                   "Set it in Space Settings → Variables."
        )

    try:
        # Import and run baseline
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from baseline.inference import run_baseline_all_tasks

        results = run_baseline_all_tasks(env, api_key)
        return {
            "status": "completed",
            "scores": results,
        }
    except ImportError:
        # If baseline module not available, return manual instructions
        return {
            "status": "manual",
            "message": "Run baseline/inference.py separately with OPENAI_API_KEY set.",
            "command": "OPENAI_API_KEY=your_key python baseline/inference.py",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Baseline failed: {str(e)}")


@app.get("/projects")
async def list_projects():
    """List all available project scenarios."""
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    return {"projects": env.get_project_list()}


# ══════════════════════════════════════════════════════
#  MAIN (for local development)
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))

    print(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "server.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=True,
    )