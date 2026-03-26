from models import (
    TeamMember, TaskItem, 
    PlannerObservation, PlannerAction, 
    PlannerState, StepResult, GraderResult
)

# Test TeamMember
alice = TeamMember(
    name="Alice",
    role="Senior Backend Developer",
    skills=["python", "django", "postgresql"],
    experience_years=7,
    availability_percent=80,
    seniority="senior"
)
print(f"✅ TeamMember created: {alice.name} ({alice.role})")

# Test TaskItem
task = TaskItem(
    name="Implement OAuth",
    assignee="Alice",
    estimated_days=3.0,
    priority=1,
    depends_on=[],
    category="backend"
)
print(f"✅ TaskItem created: {task.name}")

# Test PlannerAction
action = PlannerAction(
    tasks=[task],
    risks=["Tight deadline"],
    sprint_summary="Week 1: Backend work"
)
print(f"✅ PlannerAction created with {len(action.tasks)} tasks")

# Test PlannerObservation
obs = PlannerObservation(
    project_id="proj_001",
    project_name="Auth System",
    project_description="Build a user authentication system",
    project_requirements=["OAuth login", "Email verification"],
    project_constraints=["Must use OAuth 2.0"],
    team_members=[alice],
    deadline_days=10,
    task_type="easy",
    task_instructions="Break the project into tasks."
)
print(f"✅ PlannerObservation created for: {obs.project_name}")

# Test StepResult
result = StepResult(
    observation=obs,
    reward=0.75,
    done=True,
    info={"grader": "passed"}
)
print(f"✅ StepResult created: reward={result.reward}, done={result.done}")

# Test PlannerState
state = PlannerState(
    episode_id="ep_001",
    step_count=1,
    current_task="easy",
    project_id="proj_001"
)
print(f"✅ PlannerState created: episode={state.episode_id}")

# Test GraderResult
grade = GraderResult(
    score=0.85,
    breakdown={"task_coverage": 0.9, "skill_match": 0.8},
    feedback="Good task breakdown! Missed testing task.",
    penalties=["Missing test task"],
    bonuses=["Identified deployment task"]
)
print(f"✅ GraderResult created: score={grade.score}")

print("\n🎉 ALL MODELS WORKING PERFECTLY!")
print("📁 models.py is READY!")
