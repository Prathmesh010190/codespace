from models import PlannerAction, GraderResult


class EasyGrader:
    """
    Grades the EASY task: Project Task Breakdown.
    
    The agent only needs to identify tasks — no assignment or estimation.
    
    Usage:
        grader = EasyGrader(ground_truth)
        result = grader.grade(action)
        print(result.score)  # 0.0 to 1.0
    """

    def __init__(self, ground_truth: dict):
        """
        Args:
            ground_truth: Dict with 'required_tasks' list from ground_truth.json
        """
        self.ground_truth = ground_truth
        self.required_tasks = ground_truth["required_tasks"]

    def grade(self, action: PlannerAction) -> GraderResult:
        """
        Grade the agent's task breakdown.
        
        Args:
            action: The agent's submitted plan
            
        Returns:
            GraderResult with score, breakdown, and feedback
        """
        submitted_tasks = action.tasks

        # Empty submission
        if not submitted_tasks:
            return GraderResult(
                score=0.0,
                breakdown={"task_coverage": 0.0},
                feedback="No tasks submitted.",
                penalties=["Empty submission"],
            )

        # Calculate task coverage
        matched = []
        unmatched = []

        for req in self.required_tasks:
            keyword = req["keyword"].lower()
            desc_words = [w for w in req["description"].lower().split() if len(w) > 3]

            found = False
            for task in submitted_tasks:
                name = task.name.lower()
                if keyword in name or any(w in name for w in desc_words):
                    found = True
                    break

            if found:
                matched.append(req["keyword"])
            else:
                unmatched.append(req["description"])

        coverage = len(matched) / len(self.required_tasks) if self.required_tasks else 0

        # Check duplicates
        names = [t.name.lower().strip() for t in submitted_tasks]
        duplicates = len(names) - len(set(names))
        penalty = duplicates * 0.05

        # Bonus for extra useful tasks
        bonus = 0.0
        bonus_items = []
        for task in submitted_tasks:
            name = task.name.lower()
            for kw in ["test", "document", "review", "deploy", "monitor"]:
                if kw in name:
                    bonus += 0.02
                    bonus_items.append(f"'{kw}' task identified")
                    break
        bonus = min(bonus, 0.15)

        # Final score
        score = max(0.0, min(1.0, coverage + bonus - penalty))

        feedback = (
            f"Coverage: {len(matched)}/{len(self.required_tasks)} ({coverage:.0%}). "
        )
        if unmatched:
            feedback += f"Missing: {', '.join(unmatched[:3])}. "
        feedback += f"Score: {score:.2f}/1.00"

        return GraderResult(
            score=round(score, 4),
            breakdown={
                "task_coverage": round(coverage, 4),
                "bonus": round(bonus, 4),
                "penalty": round(penalty, 4),
                "tasks_submitted": len(submitted_tasks),
                "requirements_matched": len(matched),
                "requirements_total": len(self.required_tasks),
            },
            feedback=feedback,
            penalties=[f"{duplicates} duplicates"] if duplicates else [],
            bonuses=bonus_items,
        )