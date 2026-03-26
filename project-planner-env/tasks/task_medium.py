MEDIUM_TASK = {
    "task_type": "medium",
    "name": "Plan and Assign",
    "description": (
        "Break the project into tasks, assign each to a team member "
        "based on their skills and availability, and estimate effort "
        "in working days. Must respect team capacity and deadline."
    ),
    "required_fields": {
        "tasks": [
            {"field": "name", "type": "string", "required": True,
             "description": "Short descriptive name of the task"},
            {"field": "assignee", "type": "string", "required": True,
             "description": "Name of the team member assigned"},
            {"field": "estimated_days", "type": "float", "required": True,
             "description": "Estimated working days to complete"}
        ]
    },
    "optional_fields": {
        "tasks": [
            {"field": "priority", "type": "integer", "required": False,
             "description": "Priority order (1 = highest)"},
            {"field": "category", "type": "string", "required": False,
             "description": "Task category: backend, frontend, testing, design, devops"}
        ]
    },
    "scoring_criteria": {
        "task_coverage": {
            "weight": "40%",
            "description": "Percentage of required features covered"
        },
        "skill_match": {
            "weight": "25%",
            "description": "Do assignees have the right skills for their tasks?"
        },
        "availability": {
            "weight": "20%",
            "description": "Is any team member assigned more work than their availability?"
        },
        "deadline_feasibility": {
            "weight": "15%",
            "description": "Does the total plan fit within the project deadline?"
        }
    },
    "difficulty": "Intermediate",
    "expected_scores": {
        "random_agent": "5-15%",
        "basic_llm": "35-50%",
        "good_llm": "55-70%",
        "frontier_llm": "70-85%"
    },
    "example_action": {
        "tasks": [
            {"name": "Design API endpoints", "assignee": "Alice",
             "estimated_days": 2, "category": "backend"},
            {"name": "Build frontend components", "assignee": "Bob",
             "estimated_days": 3, "category": "frontend"},
            {"name": "Write integration tests", "assignee": "Charlie",
             "estimated_days": 2, "category": "testing"}
        ]
    }
}