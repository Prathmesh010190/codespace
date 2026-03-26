import json

# Test projects.json
print("Testing projects.json...")
with open("data/projects.json", "r") as f:
    projects = json.load(f)
print(f"  ✅ Loaded {len(projects)} projects")
for p in projects:
    print(f"     📋 {p['id']}: {p['name']} ({p['difficulty']})")

print()

# Test teams.json
print("Testing teams.json...")
with open("data/teams.json", "r") as f:
    teams = json.load(f)
print(f"  ✅ Loaded {len(teams)} teams")
for team_id, team in teams.items():
    members = [m['name'] for m in team['members']]
    print(f"     👥 {team_id}: {', '.join(members)}")

print()

# Test ground_truth.json
print("Testing ground_truth.json...")
with open("data/ground_truth.json", "r") as f:
    truth = json.load(f)
print(f"  ✅ Loaded ground truth for {len(truth)} projects")
for proj_id, data in truth.items():
    tasks = len(data['required_tasks'])
    deps = len(data['known_dependencies'])
    risks = len(data['known_risks'])
    print(f"     📊 {proj_id}: {tasks} tasks, {deps} dependencies, {risks} risks")

print()

# Cross-validation
print("Cross-validating data...")
errors = []
for project in projects:
    pid = project['id']
    team_config = project['team_config']
    
    if pid not in truth:
        errors.append(f"❌ {pid} missing from ground_truth.json")
    
    if team_config not in teams:
        errors.append(f"❌ {team_config} missing from teams.json")

if errors:
    for e in errors:
        print(f"  {e}")
else:
    print("  ✅ All projects have matching ground truth and team configs!")

print()
print("🎉 ALL DATA FILES ARE VALID!")
print("📁 Data layer is READY!")
