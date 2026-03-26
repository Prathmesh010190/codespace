# 🏗️ ProjectPlannerEnv — OpenEnv Environment

An OpenEnv environment where AI agents act as **Project Managers**. Agents receive project briefs with team information and create sprint plans that are evaluated by automated graders.

## 🎯 Motivation

Every tech company does sprint planning — breaking projects into tasks, assigning team members, estimating effort, and managing dependencies. This environment simulates that real-world task, providing a structured way to train and evaluate AI agents on project management skills.

**Real-world utility:** Project planning is done daily at every software company. An AI agent that masters this environment could assist with actual sprint planning, resource allocation, and deadline management.

## 🏗️ Architecture
Agent Environment (Docker/HF Space)
┌──────────┐ ┌──────────────────────────────┐
│ LLM/AI │ reset() │ ProjectPlannerEnvironment │
│ Agent │ ──────────────→ │ ├── 10 project scenarios │
│ │ ←────────────── │ ├── 5 team configurations │
│ │ observation │ ├── 3 difficulty levels │
│ │ │ └── Automated graders │
│ │ step(plan) │ │
│ │ ──────────────→ │ Grade plan → score 0.0-1.0 │
│ │ ←────────────── │ │
│ │ reward+done │ │
└──────────┘ └──────────────────────────────┘


## 📋 Task Descriptions

### Task 1: Easy — Task Breakdown
- **Objective:** Break a project into individual tasks/subtasks
- **Required fields:** `tasks[].name`
- **Scoring:** Based on coverage of project requirements
- **Expected scores:** Basic LLM: 60-75%, Frontier LLM: 90-98%

### Task 2: Medium — Plan and Assign
- **Objective:** Break down + assign to team members + estimate effort
- **Required fields:** `tasks[].name`, `tasks[].assignee`, `tasks[].estimated_days`
- **Scoring:** Coverage (40%) + Skill match (25%) + Availability (20%) + Deadline (15%)
- **Expected scores:** Basic LLM: 35-50%, Frontier LLM: 70-85%

### Task 3: Hard — Complete Sprint Plan
- **Objective:** Full sprint plan with dependencies, risks, and summary
- **Required fields:** All task fields + `risks` + `sprint_summary`
- **Scoring:** Coverage (25%) + Skills (20%) + Availability (15%) + Dependencies (15%) + Risks (10%) + Summary (5%) + Deadline (10%)
- **Expected scores:** Basic LLM: 20-35%, Frontier LLM: 50-70%

## 🎮 Action Space

```json
{
    "tasks": [
        {
            "name": "string — task name",
            "assignee": "string — team member name (medium/hard)",
            "estimated_days": "float — effort in days (medium/hard)",
            "priority": "int — priority order (hard)",
            "depends_on": ["string — dependency task names (hard)"],
            "category": "string — backend/frontend/testing/design/devops"
        }
    ],
    "risks": ["string — identified risks (hard)"],
    "sprint_summary": "string — overall plan summary (hard)"
}
