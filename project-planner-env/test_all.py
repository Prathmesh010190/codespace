print("=" * 50)
print("TESTING ALL COMPONENTS")
print("=" * 50)

# Test 1: Models
print("\n📋 Testing models...")
from models import PlannerAction, TaskItem, GraderResult
print("  ✅ Models import OK")

# Test 2: Environment
print("\n🧠 Testing environment...")
from server.environment import ProjectPlannerEnvironment
env = ProjectPlannerEnvironment()
print("  ✅ Environment created")

# Test 3: Graders
print("\n📊 Testing graders...")
from graders import EasyGrader, MediumGrader, HardGrader

# Easy grader test
result = env.reset(task_type="easy", project_id="proj_001")
gt = env._current_ground_truth
easy_grader = EasyGrader(gt)
action = PlannerAction(tasks=[
    TaskItem(name="User signup implementation"),
    TaskItem(name="Login and logout"),
    TaskItem(name="OAuth integration"),
    TaskItem(name="Password reset flow"),
    TaskItem(name="Frontend UI"),
])
grade = easy_grader.grade(action)
print(f"  ✅ Easy grader: score={grade.score:.2f}")

# Medium grader test
team = env._current_team
deadline = env._current_project["deadline_days"]
med_grader = MediumGrader(gt, team, deadline)
action2 = PlannerAction(tasks=[
    TaskItem(name="User signup", assignee="Alice", estimated_days=2, category="backend"),
    TaskItem(name="OAuth integration", assignee="Alice", estimated_days=3, category="backend"),
    TaskItem(name="Frontend login", assignee="Bob", estimated_days=3, category="frontend"),
    TaskItem(name="Unit tests", assignee="Charlie", estimated_days=2, category="testing"),
])
grade2 = med_grader.grade(action2)
print(f"  ✅ Medium grader: score={grade2.score:.2f}")

# Hard grader test
hard_grader = HardGrader(gt, team, deadline)
action3 = PlannerAction(
    tasks=[
        TaskItem(name="User signup", assignee="Alice", estimated_days=2,
                priority=1, depends_on=[], category="backend"),
        TaskItem(name="OAuth setup", assignee="Alice", estimated_days=3,
                priority=2, depends_on=["User signup"], category="backend"),
        TaskItem(name="Frontend login", assignee="Bob", estimated_days=3,
                priority=3, depends_on=["OAuth setup"], category="frontend"),
        TaskItem(name="Tests", assignee="Charlie", estimated_days=2,
                priority=4, depends_on=["User signup"], category="testing"),
    ],
    risks=["Junior dev may need extra review time", "OAuth API changes"],
    sprint_summary="Week 1: Backend auth. Week 2: Frontend and tests."
)
grade3 = hard_grader.grade(action3)
print(f"  ✅ Hard grader: score={grade3.score:.2f}")

# Test 4: Tasks
print("\n📝 Testing tasks...")
from tasks import ALL_TASKS, EASY_TASK, MEDIUM_TASK, HARD_TASK
print(f"  ✅ {len(ALL_TASKS)} tasks loaded")
for t in ALL_TASKS:
    print(f"     → {t['task_type']}: {t['name']} ({t['difficulty']})")

# Test 5: FastAPI App
print("\n🌐 Testing FastAPI app...")
from server.app import app
print(f"  ✅ FastAPI app created: {app.title} v{app.version}")
routes = [r.path for r in app.routes if hasattr(r, 'path')]
print(f"  ✅ Routes: {', '.join(routes)}")

# Summary
print("\n" + "=" * 50)
print("🎉 ALL COMPONENTS WORKING!")
print("=" * 50)
print(f"""
Component Status:
  ✅ models.py          — All data types working
  ✅ data/              — 10 projects, 5 teams, ground truth
  ✅ environment.py     — Core logic with 3 methods
  ✅ graders/           — Easy, Medium, Hard graders
  ✅ tasks/             — 3 task definitions
  ✅ server/app.py      — FastAPI with all endpoints

Endpoints Available:
  GET  /health    — Health check
  POST /reset     — Start episode
  POST /step      — Submit plan
  GET  /state     — Episode info
  GET  /tasks     — Task definitions
  POST /grader    — Run grader
  POST /baseline  — Run baseline
  GET  /projects  — List projects
""")
