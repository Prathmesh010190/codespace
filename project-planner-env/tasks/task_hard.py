HARD_TASK = {
    "task_type": "hard",
    "name": "Complete Sprint Plan",
    "description": (
        "Create a complete sprint plan: break into tasks, estimate effort, "
        "assign team members, define dependencies, set priorities, identify "
        "risks, and write a sprint summary. Must handle resource conflicts "
        "and respect all constraints."
    ),
    "required_fields": {
        "tasks": [
            {"field": "name", "type": "string", "required": True,
             "description": "Short descriptive name"},
            {"field": "assignee", "type": "string", "required": True,
             "description": "Assigned team member"},
            {"field": "estimated_days", "type": "float", "required": True,
             "description": "Estimated working days"},
            {"field": "priority", "type": "integer", "required": True,
             "description": "Priority order (1 = highest)"},
            {"field": "depends_on", "type": "list[string]", "required": True,
             "description": "List of task names this depends on"},
            {"field": "category", "type": "string", "required": True,
             "description": "Category: backend, frontend, testing, design, devops"}
        ],
        "risks": {
            "type": "list[string]",
            "required": True,
            "description": "List of identified project risks"
        },
        "sprint_summary": {
            "type": "string",
            "required": True,
            "description": "Overall sprint plan summary describing execution approach"
        }
    },
    "optional_fields": {},
    "scoring_criteria": {
        "task_coverage": {"weight": "25%", "description": "Features covered"},
        "skill_match": {"weight": "20%", "description": "Skill-assignment fit"},
        "availability": {"weight": "15%", "description": "Capacity compliance"},
        "dependencies": {"weight": "15%", "description": "Dependency correctness"},
        "risk_identification": {"weight": "10%", "description": "Risks identified"},
        "sprint_summary": {"weight": "5%", "description": "Summary quality"},
        "deadline_feasibility": {"weight": "10%", "description": "Timeline fit"}
    },
    "difficulty": "Advanced",
    "expected_scores": {
        "random_agent": "2-8%",
        "basic_llm": "20-35%",
        "good_llm": "40-55%",
        "frontier_llm": "50-70%"
    },
    "example_action": {
        "tasks": [
            {"name": "Design system architecture", "assignee": "Alice",
             "estimated_days": 2, "priority": 1, "depends_on": [],
             "category": "backend"},
            {"name": "Implement core API", "assignee": "Alice",
             "estimated_days": 4, "priority": 2,
             "depends_on": ["Design system architecture"],
             "category": "backend"},
            {"name": "Build frontend UI", "assignee": "Bob",
             "estimated_days": 3, "priority": 3,
             "depends_on": ["Implement core API"],
             "category": "frontend"}
        ],
        "risks": [
            "Tight deadline with limited senior availability",
            "Integration complexity between services"
        ],
        "sprint_summary": "Week 1: Architecture and core API. Week 2: Frontend and testing."
    }
}