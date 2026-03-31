import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

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

env: Optional[ProjectPlannerEnvironment] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
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
        "An OpenEnv environment where AI agents act as Project Managers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

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
    task_type: str = "easy"
    project_id: Optional[str] = None


class StepRequest(BaseModel):
    action: PlannerAction


class GraderRequest(BaseModel):
    task_type: str = "easy"
    project_id: str = "proj_001"
    action: PlannerAction


class HealthResponse(BaseModel):
    status: str = "healthy"
    environment: str = "ProjectPlannerEnv"
    version: str = "1.0.0"


# ══════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint - required for HF Spaces."""
    return {
        "status": "running",
        "environment": "ProjectPlannerEnv",
        "version": "1.0.0",
        "endpoints": [
            "/health", "/reset", "/step", "/state",
            "/tasks", "/projects", "/grader", "/baseline"
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


@app.post("/reset", response_model=StepResult)
async def reset(request: ResetRequest):
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    try:
        result = env.reset(task_type=request.task_type, project_id=request.project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step", response_model=StepResult)
async def step(request: StepRequest):
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
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    return env.state()


@app.get("/tasks")
async def get_tasks():
    """Return available task difficulties and the expected action schema."""
    return {
        "available_tasks": [
            {
                "task_id": "easy",
                "name": "Simple Web App Project Planning",
                "description": "Plan a small portfolio website with 2 team members",
                "difficulty": "easy",
                "team_size": 2,
                "deadline_days": 14
            },
            {
                "task_id": "medium",
                "name": "E-Commerce MVP Planning",
                "description": "Plan an e-commerce platform with 4 team members",
                "difficulty": "medium",
                "team_size": 4,
                "deadline_days": 30
            },
            {
                "task_id": "hard",
                "name": "Real-Time SaaS Platform Planning",
                "description": "Plan a collaborative project management SaaS with 6 team members",
                "difficulty": "hard",
                "team_size": 6,
                "deadline_days": 45
            }
        ],
        "action_schema": {
            "tasks": [
                {
                    "name": "string",
                    "assignee": "string",
                    "estimated_days": "int (1-30)",
                    "priority": "int (1-5)",
                    "depends_on": ["list of task names"],
                    "category": "backend|frontend|design|testing|devops|research"
                }
            ],
            "risks": ["list of risk strings"],
            "sprint_summary": "string"
        },
        "categories": ["backend", "frontend", "design", "testing", "devops", "research"]
    }


@app.post("/grader")
async def run_grader(request: GraderRequest):
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    try:
        env.reset(task_type=request.task_type, project_id=request.project_id)
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


@app.get("/grader")
async def get_grader():
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    if hasattr(env, 'last_grader_result') and env.last_grader_result is not None:
        result = env.last_grader_result
        if hasattr(result, 'dict'):
            return result.dict()
        return result
    return {"error": "No completed episode yet.", "score": None}


@app.post("/baseline")
async def run_baseline():
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")

    from baseline.inference import get_plan_for_difficulty
    from models import PlannerAction, TaskItem

    results = {}
    for difficulty in ["easy", "medium", "hard"]:
        try:
            env.reset(task_type=difficulty)
            plan_data = get_plan_for_difficulty(difficulty)
            action = plan_data.get("action", plan_data)
            task_items = [
                TaskItem(
                    name=t["name"],
                    assignee=t.get("assignee", "Alice"),
                    estimated_days=t.get("estimated_days", 2),
                    priority=t.get("priority", 2),
                    depends_on=t.get("depends_on", []),
                    category=t.get("category", "backend")
                ) for t in action["tasks"]
            ]
            planner_action = PlannerAction(
                tasks=task_items,
                risks=action.get("risks", ["Unknown risk"]),
                sprint_summary=action.get("sprint_summary", "Sprint plan")
            )
            step_result = env.step(planner_action)
            score = float(getattr(step_result, 'reward', getattr(step_result, 'score', 0.0)))
            results[difficulty] = {"score": round(score, 4), "difficulty": difficulty}
        except Exception as e:
            results[difficulty] = {"score": 0.0, "difficulty": difficulty, "error": str(e)}

    avg_score = sum(r.get("score", 0.0) for r in results.values()) / 3
    return {"status": "completed", "baseline_scores": results, "average_score": round(avg_score, 4)}


@app.get("/projects")
async def list_projects():
    global env
    if env is None:
        raise HTTPException(status_code=500, detail="Environment not initialized")
    return {"projects": env.get_project_list()}


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, workers=1, reload=True)
