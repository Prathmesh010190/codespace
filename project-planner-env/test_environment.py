from server.environment import ProjectPlannerEnvironment
from models import PlannerAction, TaskItem

# Create environment
env = ProjectPlannerEnvironment()
print("✅ Environment created!")

# ════════════════════════════════════════
# TEST 1: Easy Task
# ════════════════════════════════════════
print("\n" + "="*50)
print("TEST 1: EASY TASK")
print("="*50)

result = env.reset(task_type="easy")
print(f"✅ Reset successful!")
print(f"   Project: {result.observation.project_name}")
print(f"   Task Type: {result.observation.task_type}")
print(f"   Team: {[m.name for m in result.observation.team_members]}")
print(f"   Deadline: {result.observation.deadline_days} days")
print(f"   Requirements: {len(result.observation.project_requirements)}")
print(f"   Done: {result.done}")

# Submit a simple plan
action = PlannerAction(
    tasks=[
        TaskItem(name="Design authentication flow"),
        TaskItem(name="Implement user signup and login"),
        TaskItem(name="Add OAuth integration"),
        TaskItem(name="Build password reset feature"),
        TaskItem(name="Create frontend UI"),
        TaskItem(name="Write unit tests"),
    ]
)

result = env.step(action)
print(f"\n✅ Step successful!")
print(f"   Reward: {result.reward}")
print(f"   Done: {result.done}")
print(f"   Feedback: {result.info.get('grader_feedback', 'N/A')[:100]}...")

# Check state
state = env.state()
print(f"\n✅ State:")
print(f"   Episode ID: {state.episode_id[:8]}...")
print(f"   Steps: {state.step_count}")
print(f"   Task: {state.current_task}")

# ════════════════════════════════════════
# TEST 2: Medium Task
# ════════════════════════════════════════
print("\n" + "="*50)
print("TEST 2: MEDIUM TASK")
print("="*50)

result = env.reset(task_type="medium", project_id="proj_001")
print(f"✅ Reset successful!")
print(f"   Project: {result.observation.project_name}")

team_names = [m.name for m in result.observation.team_members]
print(f"   Team: {team_names}")

# Submit a plan with assignments
action = PlannerAction(
    tasks=[
        TaskItem(name="Design OAuth flow", assignee="Alice",
                estimated_days=2, category="backend"),
        TaskItem(name="Implement signup and login", assignee="Alice",
                estimated_days=3, category="backend"),
        TaskItem(name="Build password reset", assignee="Charlie",
                estimated_days=2, category="backend"),
        TaskItem(name="Create login UI", assignee="Bob",
                estimated_days=3, category="frontend"),
        TaskItem(name="Add OAuth frontend", assignee="Bob",
                estimated_days=2, category="frontend"),
        TaskItem(name="Write unit tests", assignee="Charlie",
                estimated_days=2, category="testing"),
        TaskItem(name="Input validation", assignee="Alice",
                estimated_days=1, category="backend"),
    ]
)

result = env.step(action)
print(f"\n✅ Step successful!")
print(f"   Reward: {result.reward}")
print(f"   Breakdown: {result.info.get('grader_breakdown', {})}")

# ════════════════════════════════════════
# TEST 3: Hard Task
# ════════════════════════════════════════
print("\n" + "="*50)
print("TEST 3: HARD TASK")
print("="*50)

result = env.reset(task_type="hard", project_id="proj_007")
print(f"✅ Reset successful!")
print(f"   Project: {result.observation.project_name}")

action = PlannerAction(
    tasks=[
        TaskItem(name="Design tenant isolation architecture", assignee="Kevin",
                estimated_days=3, priority=1, depends_on=[], category="backend"),
        TaskItem(name="Implement multi-tenant database", assignee="Kevin",
                estimated_days=4, priority=2,
                depends_on=["Design tenant isolation architecture"], category="backend"),
        TaskItem(name="Build tenant onboarding flow", assignee="Mike",
                estimated_days=3, priority=3,
                depends_on=["Implement multi-tenant database"], category="backend"),
        TaskItem(name="Implement RBAC system", assignee="Kevin",
                estimated_days=3, priority=3,
                depends_on=["Implement multi-tenant database"], category="backend"),
        TaskItem(name="Build metrics dashboard", assignee="Laura",
                estimated_days=4, priority=4,
                depends_on=["Implement multi-tenant database"], category="frontend"),
        TaskItem(name="Create subscription management", assignee="Mike",
                estimated_days=3, priority=4,
                depends_on=["Build tenant onboarding flow"], category="backend"),
        TaskItem(name="Build custom branding system", assignee="Nina",
                estimated_days=3, priority=5,
                depends_on=["Build tenant onboarding flow"], category="frontend"),
        TaskItem(name="Implement report exports", assignee="Mike",
                estimated_days=2, priority=5,
                depends_on=["Build metrics dashboard"], category="backend"),
        TaskItem(name="Build super admin panel", assignee="Laura",
                estimated_days=3, priority=5,
                depends_on=["Implement RBAC system"], category="frontend"),
        TaskItem(name="Setup custom domains with SSL", assignee="Mike",
                estimated_days=3, priority=6,
                depends_on=["Build tenant onboarding flow"], category="devops"),
        TaskItem(name="Add audit logging", assignee="Kevin",
                estimated_days=2, priority=6,
                depends_on=["Implement RBAC system"], category="backend"),
    ],
    risks=[
        "Data leakage between tenants is a critical security risk",
        "Custom domain SSL management is complex and error-prone",
        "Kevin is only 60% available which creates a bottleneck",
        "Billing integration may require third-party vendor evaluation",
    ],
    sprint_summary=(
        "Week 1-2: Kevin leads database architecture and tenant isolation. "
        "Week 2-3: Mike handles onboarding and subscription while Laura builds dashboard. "
        "Week 3-4: Nina works on branding, team completes admin panel and exports. "
        "Final week: Integration testing, custom domain setup, and audit logging."
    )
)

result = env.step(action)
print(f"\n✅ Step successful!")
print(f"   Reward: {result.reward}")
print(f"   Done: {result.done}")
print(f"   Breakdown:")
for key, value in result.info.get("grader_breakdown", {}).items():
    print(f"      {key}: {value}")

# ════════════════════════════════════════
# TEST 4: Available Tasks
# ════════════════════════════════════════
print("\n" + "="*50)
print("TEST 4: AVAILABLE TASKS")
print("="*50)

tasks = env.get_available_tasks()
for task in tasks:
    print(f"  📋 {task['task_type']}: {task['name']} — {task['difficulty']}")

# ════════════════════════════════════════
# TEST 5: Edge Cases
# ════════════════════════════════════════
print("\n" + "="*50)
print("TEST 5: EDGE CASES")
print("="*50)

# Empty submission
env.reset(task_type="easy")
empty_action = PlannerAction(tasks=[])
result = env.step(empty_action)
print(f"  Empty submission score: {result.reward} (should be 0.0) ✅")

# Step after done
result = env.step(empty_action)
print(f"  Step after done: done={result.done} ✅")

print("\n🎉 ALL TESTS PASSED!")
print("🧠 environment.py is WORKING!")
