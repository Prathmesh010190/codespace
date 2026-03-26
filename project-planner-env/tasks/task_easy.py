EASY_TASK = {
    "task_type": "easy",
    "name": "Task Breakdown",
    "description": (
        "Break the project into individual tasks/subtasks. "
        "Each task should be a concrete, actionable work item that "
        "covers the project requirements. No assignment or time "
        "estimation needed."
    ),
    "required_fields": {
        "tasks": [
            {"field": "name", "type": "string", "required": True,
             "description": "Short descriptive name of the task"}
        ]
    },
    "optional_fields": {
        "tasks": [
            {"field": "category", "type": "string", "required": False,
             "description": "Task category: backend, frontend, testing, design, devops"}
        ]
    },
    "scoring_criteria": {
        "task_coverage": {
            "weight": "85%",
            "description": "Percentage of required project features covered by submitted tasks"
        },
        "bonus": {
            "weight": "up to 15%",
            "description": "Bonus for identifying non-obvious tasks like testing, documentation"
        },
        "penalty": {
            "weight": "-5% each",
            "description": "Penalty for duplicate or clearly irrelevant tasks"
        }
    },
    "difficulty": "Beginner",
    "expected_scores": {
        "random_agent": "10-20%",
        "basic_llm": "60-75%",
        "good_llm": "80-90%",
        "frontier_llm": "90-98%"
    },
    "example_action": {
        "tasks": [
            {"name": "Design database schema", "category": "backend"},
            {"name": "Implement user authentication API", "category": "backend"},
            {"name": "Build login and signup pages", "category": "frontend"},
            {"name": "Write unit tests for API", "category": "testing"},
            {"name": "Set up CI/CD pipeline", "category": "devops"}
        ]
    }
}