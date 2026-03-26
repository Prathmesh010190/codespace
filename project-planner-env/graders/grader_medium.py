from models import PlannerAction, GraderResult


class MediumGrader:
    """
    Grades the MEDIUM task: Plan and Assign.
    
    Agent must break project into tasks, assign team members,
    and estimate effort — all while respecting constraints.
    """

    def __init__(self, ground_truth: dict, team: dict, deadline_days: int):
        """
        Args:
            ground_truth: Dict with 'required_tasks' from ground_truth.json
            team: Team dict with 'members' list from teams.json
            deadline_days: Project deadline in working days
        """
        self.ground_truth = ground_truth
        self.required_tasks = ground_truth["required_tasks"]
        self.team = team
        self.deadline = deadline_days
        self.team_lookup = {
            m["name"].lower(): m for m in team["members"]
        }

    def grade(self, action: PlannerAction) -> GraderResult:
        """Grade the agent's plan with assignments and estimates."""
        submitted = action.tasks
        penalties = []
        bonuses = []

        if not submitted:
            return GraderResult(
                score=0.0, breakdown={},
                feedback="No tasks submitted.", penalties=["Empty submission"],
            )

        # 1. Coverage (40%)
        matched = 0
        for req in self.required_tasks:
            kw = req["keyword"].lower()
            desc_words = [w for w in req["description"].lower().split() if len(w) > 3]
            for task in submitted:
                name = task.name.lower()
                if kw in name or any(w in name for w in desc_words):
                    matched += 1
                    break
        coverage = matched / len(self.required_tasks) if self.required_tasks else 0

        # 2. Skill Match (25%)
        skill_ok = 0
        with_assignee = 0
        for task in submitted:
            if task.assignee:
                with_assignee += 1
                aname = task.assignee.lower()
                if aname in self.team_lookup:
                    member = self.team_lookup[aname]
                    skills = [s.lower() for s in member["skills"]]
                    cat = (task.category or "").lower()

                    has_skill = self._check_skill_match(cat, skills, task.name)
                    if has_skill:
                        skill_ok += 1
                    else:
                        penalties.append(f"Skill mismatch: {task.assignee} for '{task.name}'")
                else:
                    penalties.append(f"Unknown member: {task.assignee}")

        skill_score = skill_ok / with_assignee if with_assignee > 0 else 0

        # 3. Availability (20%)
        load = {}
        for task in submitted:
            if task.assignee and task.estimated_days:
                name = task.assignee.lower()
                load[name] = load.get(name, 0.0) + task.estimated_days

        ok_count = 0
        over_count = 0
        for name, days in load.items():
            if name in self.team_lookup:
                avail = self.deadline * (self.team_lookup[name]["availability_percent"] / 100.0)
                if days <= avail:
                    ok_count += 1
                else:
                    over_count += 1
                    penalties.append(f"Overloaded: {name} ({days:.1f}/{avail:.1f} days)")

        total = ok_count + over_count
        avail_score = ok_count / total if total > 0 else 0

        # 4. Deadline (15%)
        total_est = sum(t.estimated_days for t in submitted if t.estimated_days) or 0
        total_cap = sum(
            self.deadline * (m["availability_percent"] / 100.0)
            for m in self.team["members"]
        )
        if total_est > 0 and total_est <= total_cap:
            deadline_score = 1.0
            bonuses.append("Plan fits within capacity")
        elif total_est > 0:
            deadline_score = max(0.0, total_cap / total_est)
        else:
            deadline_score = 0.0
            penalties.append("No estimates provided")

        # Final
        score = (coverage * 0.40 + skill_score * 0.25 +
                 avail_score * 0.20 + deadline_score * 0.15)
        score = max(0.0, min(1.0, score))

        feedback = (
            f"Coverage: {matched}/{len(self.required_tasks)} ({coverage:.0%}). "
            f"Skills: {skill_score:.0%}. Availability: {avail_score:.0%}. "
            f"Deadline: {'OK' if deadline_score >= 0.8 else 'Tight'}. "
            f"Score: {score:.2f}/1.00."
        )

        return GraderResult(
            score=round(score, 4),
            breakdown={
                "task_coverage": round(coverage, 4),
                "skill_match": round(skill_score, 4),
                "availability": round(avail_score, 4),
                "deadline_feasibility": round(deadline_score, 4),
            },
            feedback=feedback,
            penalties=penalties[:5],
            bonuses=bonuses[:5],
        )

    def _check_skill_match(self, category: str, skills: list, task_name: str) -> bool:
        """Check if member skills match the task category."""
        backend = ["python", "django", "fastapi", "golang", "rest-api", "postgresql"]
        frontend = ["javascript", "react", "html", "css", "typescript"]
        testing = ["unit-testing", "integration-testing", "selenium", "manual-testing"]
        devops = ["docker", "kubernetes", "ci-cd", "linux", "monitoring"]

        if category == "backend":
            return any(s in skills for s in backend)
        elif category == "frontend":
            return any(s in skills for s in frontend)
        elif category == "testing":
            return any(s in skills for s in testing)
        elif category == "devops":
            return any(s in skills for s in devops)
        elif not category:
            return True  # No category = benefit of doubt
        return True