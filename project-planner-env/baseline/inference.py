import json
import requests

BASE_URL = "http://localhost:8000"

def get_hardcoded_plan():
    return {
        "action": {
            "tasks": [
                {"name": "Design OAuth flow", "assignee": "Alice", "estimated_days": 2, "priority": 1, "depends_on": [], "category": "backend"},
                {"name": "Implement OAuth backend", "assignee": "Alice", "estimated_days": 3, "priority": 1, "depends_on": ["Design OAuth flow"], "category": "backend"},
                {"name": "Build email verification", "assignee": "Charlie", "estimated_days": 2, "priority": 2, "depends_on": [], "category": "backend"},
                {"name": "Create password reset", "assignee": "Charlie", "estimated_days": 2, "priority": 3, "depends_on": ["Build email verification"], "category": "backend"},
                {"name": "Frontend integration", "assignee": "Bob", "estimated_days": 3, "priority": 2, "depends_on": ["Implement OAuth backend"], "category": "frontend"},
                {"name": "Testing", "assignee": "Bob", "estimated_days": 2, "priority": 3, "depends_on": ["Frontend integration"], "category": "testing"}
            ],
            "risks": ["Junior dev needs support", "OAuth complexity", "Charlie limited availability"],
            "sprint_summary": "Week 1: Backend OAuth and email by Alice and Charlie. Week 2: Frontend integration and testing by Bob."
        }
    }

def run_baseline(difficulty="easy"):
    print(f"\n🤖 Running baseline on {difficulty}...")
    print("=" * 50)

    try:
        # Reset
        obs = requests.post(f"{BASE_URL}/reset", json={"difficulty": difficulty}).json()
        print("✅ Reset successful!")

        # Submit plan
        plan = get_hardcoded_plan()
        step_result = requests.post(f"{BASE_URL}/step", json=plan).json()
        print(f"📝 Step Response: {json.dumps(step_result, indent=2)}")

        # Check state
        state = requests.get(f"{BASE_URL}/state").json()
        print(f"\n📌 State:")
        print(f"   Episode: {state.get('episode_id', 'N/A')}")
        print(f"   Step: {state.get('step_count', 'N/A')}/{state.get('max_steps', 'N/A')}")
        print(f"   🏆 Reward: {state.get('current_reward', 'N/A')}")
        print(f"   Done: {state.get('is_done', 'N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 ProjectPlannerEnv — Baseline Inference")
    print("=" * 50)
    run_baseline("easy")
    print("\n✅ Complete!")
