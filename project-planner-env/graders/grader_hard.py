from models import PlannerAction, GraderResult


class HardGrader:
    """
    Grades the HARD task: Complete Sprint Plan.
    
    Evaluates everything: tasks, assignments, estimates,
    dependencies, risks, and sprint summary.
    """

    def __init__(self, ground_truth: dict, team: dict, deadline_days: int):
        self.ground_truth = ground_truth
        self.required_tasks = ground_truth["required_tasks"]
        self.known_deps = ground_truth["known_dependencies"]
        self.known_risks = ground_truth["known_risks"]
        self.team = team
        self.deadline = deadline_days
        self.team_lookup = {
            m["name"].lower(): m for m in team["members"]
        }

    def grade(self, action: PlannerAction) -> GraderResult:
        """Grade the agent's complete sprint plan."""
        submitted = action.tasks
        penalties = []
        bonuses = []

        if not submitted:
            return GraderResult(
                score=0.0, breakdown={},
                feedback="No tasks submitted.", penalties=["Empty submission"],
            )

        # 1. Coverage (25%)
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

        # 2. Skill Match (20%)
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
                    if self._check_skill(cat, skills):
                        skill_ok += 1
                    else:
                        penalties.append(f"Skill mismatch: {task.assignee}")
                else:
                    penalties.append(f"Unknown member: {task.assignee}")
        skill_score = skill_ok / with_assignee if with_assignee > 0 else 0

        # 3. Availability (15%)
        load = {}
        for task in submitted:
            if task.assignee and task.estimated_days:
                name = task.assignee.lower()
                load[name] = load.get(name, 0.0) + task.estimated_days

        ok = sum(1 for n, d in load.items()
                 if n in self.team_lookup and
                 d <= self.deadline * (self.team_lookup[n]["availability_percent"] / 100.0))
        over = len(load) - ok
        if over > 0:
            penalties.append(f"{over} team member(s) overloaded")
        avail_score = ok / len(load) if load else 0

        # 4. Dependencies (15%)
        submitted_deps = set()
        for task in submitted:
            if task.depends_on:
                for dep in task.depends_on:
                    submitted_deps.add(dep.lower())

        has_circular = self._check_circular(submitted)
        if has_circular:
            penalties.append("Circular dependency detected!")

        dep_matches = 0
        for kd in self.known_deps:
            dep_name = kd["depends_on"].lower()
            if any(dep_name in d for d in submitted_deps):
                dep_matches += 1

        dep_score = dep_matches / len(self.known_deps) if self.known_deps else 0
        if has_circular:
            dep_score *= 0.5

        if submitted_deps and not has_circular:
            bonuses.append("Dependencies defined")

        # 5. Risks (10%)
        submitted_risks = action.risks or []
        risk_matches = 0
        if submitted_risks:
            for kr in self.known_risks:
                kw = [w for w in kr.lower().split() if len(w) > 3]
                for sr in submitted_risks:
                    if any(k in sr.lower() for k in kw):
                        risk_matches += 1
                        break

        risk_score = risk_matches / len(self.known_risks) if self.known_risks else 0
        if submitted_risks:
            risk_score = min(1.0, risk_score + min(len(submitted_risks) * 0.1, 0.3))
            bonuses.append(f"{len(submitted_risks)} risks identified")

        # 6. Summary (5%)
        summary = action.sprint_summary or ""
        summary_score = 1.0 if len(summary) > 50 else 0.5 if len(summary) > 20 else 0.0
        if not summary:
            penalties.append("No sprint summary")

        # 7. Deadline (10%)
        total_est = sum(t.estimated_days for t in submitted if t.estimated_days) or 0
        total_cap = sum(
            self.deadline * (m["availability_percent"] / 100.0)
            for m in self.team["members"]
        )
        if total_est > 0 and total_est <= total_cap:
            deadline_score = 1.0
        elif total_est > 0:
            deadline_score = max(0.0, total_cap / total_est)
        else:
            deadline_score = 0.0

        # Final
        score = (coverage * 0.25 + skill_score * 0.20 + avail_score * 0.15 +
                 dep_score * 0.15 + risk_score * 0.10 + summary_score * 0.05 +
                 deadline_score * 0.10)
        score = max(0.0, min(1.0, score))

        feedback = (
            f"Coverage: {coverage:.0%}. Skills: {skill_score:.0%}. "
            f"Availability: {avail_score:.0%}. Deps: {dep_score:.0%}. "
            f"Risks: {risk_score:.0%}. Summary: {'✓' if summary_score > 0 else '✗'}. "
            f"Score: {score:.2f}/1.00."
        )

        return GraderResult(
            score=round(score, 4),
            breakdown={
                "task_coverage": round(coverage, 4),
                "skill_match": round(skill_score, 4),
                "availability": round(avail_score, 4),
                "dependencies": round(dep_score, 4),
                "risk_identification": round(risk_score, 4),
                "sprint_summary": round(summary_score, 4),
                "deadline_feasibility": round(deadline_score, 4),
            },
            feedback=feedback,
            penalties=penalties[:5],
            bonuses=bonuses[:5],
        )

    def _check_skill(self, category: str, skills: list) -> bool:
        mapping = {
            "backend": ["python", "django", "fastapi", "golang", "rest-api", "postgresql"],
            "frontend": ["javascript", "react", "html", "css", "typescript"],
            "testing": ["unit-testing", "integration-testing", "selenium", "manual-testing"],
            "devops": ["docker", "kubernetes", "ci-cd", "linux", "monitoring"],
        }
        if category in mapping:
            return any(s in skills for s in mapping[category])
        return True

    def _check_circular(self, tasks: list) -> bool:
        graph = {}
        for t in tasks:
            name = t.name.lower()
            graph[name] = [d.lower() for d in (t.depends_on or [])]

        visited = set()
        in_stack = set()

        def dfs(node):
            if node in in_stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            in_stack.add(node)
            for nb in graph.get(node, []):
                if dfs(nb):
                    return True
            in_stack.remove(node)
            return False

        return any(dfs(n) for n in graph if n not in visited)