import os

print("🔍 FINAL PRE-SUBMISSION CHECK")
print("=" * 50)

required_files = [
    "models.py",
    "client.py",
    "openenv.yaml",
    "requirements.txt",
    "README.md",
    "data/projects.json",
    "data/teams.json",
    "data/ground_truth.json",
    "tasks/__init__.py",
    "tasks/task_easy.py",
    "tasks/task_medium.py",
    "tasks/task_hard.py",
    "graders/__init__.py",
    "graders/grader_easy.py",
    "graders/grader_medium.py",
    "graders/grader_hard.py",
    "baseline/inference.py",
    "server/__init__.py",
    "server/environment.py",
    "server/app.py",
    "server/Dockerfile",
]

print("\n📁 File Check:")
missing = []
for f in required_files:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌"
    size = os.path.getsize(f) if exists else 0
    print(f"  {status} {f} ({size} bytes)")
    if not exists:
        missing.append(f)

if missing:
    print(f"\n⚠️ Missing {len(missing)} files: {missing}")
else:
    print(f"\n✅ All {len(required_files)} files present!")

print("\n📦 Import Check:")
try:
    from models import PlannerAction, PlannerObservation, StepResult
    print("  ✅ models.py")
except Exception as e:
    print(f"  ❌ models.py: {e}")

try:
    from server.environment import ProjectPlannerEnvironment
    print("  ✅ server/environment.py")
except Exception as e:
    print(f"  ❌ server/environment.py: {e}")

try:
    from graders import EasyGrader, MediumGrader, HardGrader
    print("  ✅ graders/")
except Exception as e:
    print(f"  ❌ graders/: {e}")

try:
    from tasks import ALL_TASKS
    print(f"  ✅ tasks/ ({len(ALL_TASKS)} tasks)")
except Exception as e:
    print(f"  ❌ tasks/: {e}")

try:
    from server.app import app
    print(f"  ✅ server/app.py ({app.title})")
except Exception as e:
    print(f"  ❌ server/app.py: {e}")

print("\n🧠 Environment Check:")
try:
    env = ProjectPlannerEnvironment()
    print(f"  ✅ Created with {len(env._projects)} projects")

    from models import TaskItem
    r = env.reset(task_type="easy")
    print(f"  ✅ Easy reset: {r.observation.project_name}")

    r = env.reset(task_type="medium")
    print(f"  ✅ Medium reset: {r.observation.project_name}")

    r = env.reset(task_type="hard")
    print(f"  ✅ Hard reset: {r.observation.project_name}")

    action = PlannerAction(tasks=[TaskItem(name="Test task")])
    r = env.step(action)
    print(f"  ✅ Step + grading works (score: {r.reward})")

    s = env.state()
    print(f"  ✅ State works (episode: {s.episode_id[:8]}...)")

except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
if not missing:
    print("🎉 PROJECT IS READY!")
else:
    print(f"⚠️ Fix {len(missing)} missing files first!")
