import json
import requests

BASE_URL = "http://localhost:8000"

def get_hardcoded_plan(difficulty):
    if difficulty == "easy":
        return {
            "tasks": [
                {"name": "Design OAuth flow", "assignee": "Alice", "estimated_days": 2, "priority": "high", "depends_on": [], "skills_required": ["backend", "security"]},
                {"name": "Implement OAuth backend", "assignee": "Alice", "estimated_days": 3, "priority": "critical", "depends_on": ["Design OAuth flow"], "skills_required": ["backend"]},
                {"name": "Build email verification", "assignee": "Charlie", "estimated_days": 2, "priority": "high", "depends_on": [], "skills_required": ["backend"]},
                {"name": "Create password reset", "assignee": "Charlie", "estimated_days": 2, "priority": "medium", "depends_on": ["Build email verification"], "skills_required": ["backend"]},
                {"name": "Frontend integration", "assignee": "Bob", "estimated_days": 3, "priority": "high", "depends_on": ["Implement OAuth backend"], "skills_required": ["frontend"]},
                {"name": "Testing", "assignee": "Bob", "estimated_days": 2, "priority": "medium", "depends_on": ["Frontend integration"], "skills_required": ["testing"]}
            ],
            "risks": ["Junior developer may need support", "OAuth complexity", "Charlie limited availability"],
            "sprint_summary": "Week 1: Backend services by Alice & Charlie. Week 2: Frontend integration and testing by Bob.",
            "milestones": ["Backend Complete", "Frontend Complete", "Launch Ready"]
        }
    return {"tasks": [], "risks": [], "sprint_summary": "", "milestones": []}

def run_baseline(difficulty="easy"):
    print(f"\n🤖 Running baseline agent on {difficulty} difficulty...")
    print("=" * 50)

    # Reset environment
    try:
        obs_response = requests.post(f"{BASE_URL}/reset", json={"difficulty": difficulty})
        obs = obs_response.json()
        print(f"✅ Environment reset successfully!")
        print(f"📋 Project: {obs.get('observation', obs).get('project', {}).get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ Server not running? Error: {e}")
        print("Start server first: python -m uvicorn server.app:app --host 0.0.0.0 --port 8000")
        return

    # Get hardcoded plan
    plan = get_hardcoded_plan(difficulty)
    print(f"📝 Submitting plan with {len(plan['tasks'])} tasks...")

    # Submit plan
    result = requests.post(f"{BASE_URL}/step", json=plan)
    result_data = result.json()

    print(f"\n🏆 Score: {result_data.get('score', 'N/A')}")
    print(f"✅ Passed: {result_data.get('passed', 'N/A')}")
    print(f"📊 Breakdown:")
    for key, value in result_data.get('breakdown', {}).items():
        print(f"   {key}: {value}")
    
    if result_data.get('feedback'):
        print(f"💬 Feedback:")
        for fb in result_data['feedback']:
            print(f"   - {fb}")

    return result_data

if __name__ == "__main__":
    print("🚀 ProjectPlannerEnv — Baseline Inference")
    print("=" * 50)
    print("Using hardcoded baseline plan (no API key needed)")
    
    run_baseline("easy")
    print("\n" + "=" * 50)
    print("✅ Baseline test complete!")
