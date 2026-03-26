import json
import uuid
import random
import os
from typing import Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    TeamMember,
    PlannerObservation,
    PlannerAction,
    PlannerState,
    StepResult,
    GraderResult,
)


class ProjectPlannerEnvironment:
    

    def __init__(self):
        """
        Initialize the environment.
        Load all project data from JSON files.
        """
        # ── Load Data ──────────────────────────────────────
        self._load_data()

        # ── Episode State (reset each episode) ─────────────
        self._episode_id: Optional[str] = None
        self._step_count: int = 0
        self._max_steps: int = 3  # Agent gets up to 3 attempts
        self._is_done: bool = False
        self._current_reward: float = 0.0
        self._current_task_type: str = "easy"
        self._current_project: Optional[dict] = None
        self._current_team: Optional[dict] = None
        self._current_ground_truth: Optional[dict] = None
        self._last_feedback: Optional[str] = None
        self._best_score: float = 0.0  # Track best score across steps

    def _load_data(self):
        """
        Load projects, teams, and ground truth from JSON files.
        Looks for data files relative to this file's location.
        """
        # Find the data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        # Load projects
        with open(os.path.join(data_dir, "projects.json"), "r") as f:
            self._projects = json.load(f)

        # Load teams
        with open(os.path.join(data_dir, "teams.json"), "r") as f:
            self._teams = json.load(f)

        # Load ground truth
        with open(os.path.join(data_dir, "ground_truth.json"), "r") as f:
            self._ground_truth = json.load(f)

        # Organize projects by difficulty for easy lookup
        self._projects_by_difficulty = {
            "easy": [],
            "medium": [],
            "hard": [],
        }
        for project in self._projects:
            difficulty = project["difficulty"]
            if difficulty in self._projects_by_difficulty:
                self._projects_by_difficulty[difficulty].append(project)

    # ══════════════════════════════════════════════════════
    #  THE 3 MAIN METHODS (OpenEnv Interface)
    # ══════════════════════════════════════════════════════

    def reset(self, task_type: str = "easy", project_id: Optional[str] = None) -> StepResult:
        """
        Start a new episode.
        
        Args:
            task_type: Difficulty level - "easy", "medium", or "hard"
            project_id: Specific project to use (optional). 
                       If None, picks a random project matching the difficulty.
        
        Returns:
            StepResult with the initial observation (project brief + team info)
        
        Example:
            result = env.reset(task_type="easy")
            print(result.observation.project_description)
        """
        # ── Validate task type ─────────────────────────────
        if task_type not in ["easy", "medium", "hard"]:
            raise ValueError(f"task_type must be 'easy', 'medium', or 'hard'. Got: {task_type}")

        # ── Select a project ───────────────────────────────
        if project_id:
            # Use specific project if requested
            project = self._find_project_by_id(project_id)
            if project is None:
                raise ValueError(f"Project not found: {project_id}")
        else:
            # Pick a random project
            # For easy/medium tasks, we can use any project
            # For hard tasks, prefer harder projects
            if task_type == "hard":
                available = self._projects_by_difficulty.get("hard", [])
                if not available:
                    available = self._projects_by_difficulty.get("medium", [])
            elif task_type == "medium":
                available = self._projects_by_difficulty.get("medium", [])
                if not available:
                    available = self._projects_by_difficulty.get("easy", [])
            else:
                available = self._projects_by_difficulty.get("easy", [])
                if not available:
                    available = self._projects

            project = random.choice(available)

        # ── Get team and ground truth ──────────────────────
        team_config = project["team_config"]
        team = self._teams[team_config]
        ground_truth = self._ground_truth[project["id"]]

        # ── Reset episode state ────────────────────────────
        self._episode_id = str(uuid.uuid4())
        self._step_count = 0
        self._is_done = False
        self._current_reward = 0.0
        self._current_task_type = task_type
        self._current_project = project
        self._current_team = team
        self._current_ground_truth = ground_truth
        self._last_feedback = None
        self._best_score = 0.0

        # ── Build the observation ──────────────────────────
        observation = self._build_observation()

        # ── Return initial StepResult ──────────────────────
        return StepResult(
            observation=observation,
            reward=0.0,
            done=False,
            info={
                "message": "New episode started. Read the project brief and submit your plan.",
                "task_type": task_type,
                "project_id": project["id"],
                "episode_id": self._episode_id,
            }
        )

    def step(self, action: PlannerAction) -> StepResult:
        """
        Process the agent's project plan and return a graded result.
        
        Args:
            action: PlannerAction containing the agent's project plan
                   (tasks, risks, sprint_summary)
        
        Returns:
            StepResult with:
            - observation: Updated observation with feedback
            - reward: Score from the grader (0.0 to 1.0)
            - done: Whether the episode is over
            - info: Detailed grading breakdown
        
        Example:
            action = PlannerAction(tasks=[...], risks=[...])
            result = env.step(action)
            print(f"Score: {result.reward}")
        """
        # ── Check if episode is active ─────────────────────
        if self._is_done:
            return StepResult(
                observation=self._build_observation(),
                reward=0.0,
                done=True,
                info={"error": "Episode is already done. Call reset() to start a new one."}
            )

        if self._episode_id is None:
            return StepResult(
                observation=self._build_observation_empty(),
                reward=0.0,
                done=True,
                info={"error": "No active episode. Call reset() first."}
            )

        # ── Increment step count ───────────────────────────
        self._step_count += 1

        # ── Grade the agent's plan ─────────────────────────
        grader_result = self._grade_plan(action)

        # ── Calculate reward ───────────────────────────────
        step_reward = grader_result.score

        # Track best score (agent might improve across attempts)
        if step_reward > self._best_score:
            self._best_score = step_reward

        self._current_reward = self._best_score

        # ── Store feedback for next observation ────────────
        self._last_feedback = grader_result.feedback

        # ── Check if episode should end ────────────────────
        # Episode ends if:
        # 1. Agent got a perfect score (1.0)
        # 2. Agent used all attempts
        if step_reward >= 0.95 or self._step_count >= self._max_steps:
            self._is_done = True

        # ── Build response ─────────────────────────────────
        observation = self._build_observation()

        return StepResult(
            observation=observation,
            reward=step_reward,
            done=self._is_done,
            info={
                "grader_score": grader_result.score,
                "grader_breakdown": grader_result.breakdown,
                "grader_feedback": grader_result.feedback,
                "penalties": grader_result.penalties,
                "bonuses": grader_result.bonuses,
                "step_number": self._step_count,
                "max_steps": self._max_steps,
                "best_score": self._best_score,
                "attempts_remaining": self._max_steps - self._step_count,
            }
        )

    def state(self) -> PlannerState:
        """
        Get current episode metadata.
        
        Returns:
            PlannerState with episode information
        
        Example:
            state = env.state()
            print(f"Episode: {state.episode_id}, Steps: {state.step_count}")
        """
        return PlannerState(
            episode_id=self._episode_id or "no_active_episode",
            step_count=self._step_count,
            max_steps=self._max_steps,
            current_task=self._current_task_type,
            project_id=self._current_project["id"] if self._current_project else "none",
            is_done=self._is_done,
            current_reward=self._current_reward,
        )

    # ══════════════════════════════════════════════════════
    #  TASK & PROJECT INFO METHODS
    # ══════════════════════════════════════════════════════

    def get_available_tasks(self) -> list:
        """
        Returns list of available task types with descriptions.
        Used by the /tasks endpoint.
        """
        return [
            {
                "task_type": "easy",
                "name": "Task Breakdown",
                "description": "Break the project into individual tasks/subtasks. "
                              "No assignment or estimation needed.",
                "required_fields": ["tasks[].name"],
                "optional_fields": ["tasks[].category"],
                "scoring": "Based on coverage of required project features.",
                "difficulty": "Beginner — any LLM should score 70%+",
            },
            {
                "task_type": "medium",
                "name": "Plan and Assign",
                "description": "Break the project into tasks, estimate effort in days, "
                              "and assign each task to a team member based on their skills "
                              "and availability.",
                "required_fields": [
                    "tasks[].name",
                    "tasks[].assignee",
                    "tasks[].estimated_days",
                ],
                "optional_fields": ["tasks[].priority", "tasks[].category"],
                "scoring": "Based on task coverage, skill-assignment match, "
                          "availability compliance, and deadline feasibility.",
                "difficulty": "Intermediate — good LLMs score 50-70%",
            },
            {
                "task_type": "hard",
                "name": "Complete Sprint Plan",
                "description": "Create a complete sprint plan: break into tasks, estimate, "
                              "assign, define dependencies, set priorities, identify risks, "
                              "and write a sprint summary. Must handle resource conflicts.",
                "required_fields": [
                    "tasks[].name",
                    "tasks[].assignee",
                    "tasks[].estimated_days",
                    "tasks[].priority",
                    "tasks[].depends_on",
                    "tasks[].category",
                    "risks",
                    "sprint_summary",
                ],
                "optional_fields": [],
                "scoring": "Comprehensive evaluation of task coverage, assignments, "
                          "estimates, dependencies, risks, and overall plan quality.",
                "difficulty": "Advanced — challenges frontier models (GPT-4 scores 40-60%)",
            },
        ]

    def get_project_list(self) -> list:
        """Returns list of all available projects with basic info."""
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "difficulty": p["difficulty"],
                "deadline_days": p["deadline_days"],
                "team": p["team_config"],
                "num_requirements": len(p["requirements"]),
            }
            for p in self._projects
        ]

    # ══════════════════════════════════════════════════════
    #  INTERNAL HELPER METHODS
    # ══════════════════════════════════════════════════════

    def _find_project_by_id(self, project_id: str) -> Optional[dict]:
        """Find a project by its ID."""
        for project in self._projects:
            if project["id"] == project_id:
                return project
        return None

    def _build_observation(self) -> PlannerObservation:
        """
        Build the observation that the agent sees.
        Includes project brief, team info, and task instructions.
        """
        project = self._current_project
        team = self._current_team
        task_type = self._current_task_type

        # Build team member models
        team_members = [
            TeamMember(
                name=m["name"],
                role=m["role"],
                skills=m["skills"],
                experience_years=m["experience_years"],
                availability_percent=m["availability_percent"],
                seniority=m["seniority"],
            )
            for m in team["members"]
        ]

        # Build task-specific instructions
        task_instructions = self._get_task_instructions(task_type)

        return PlannerObservation(
            project_id=project["id"],
            project_name=project["name"],
            project_description=project["description"],
            project_requirements=project["requirements"],
            project_constraints=project["constraints"],
            team_members=team_members,
            deadline_days=project["deadline_days"],
            task_type=task_type,
            task_instructions=task_instructions,
            feedback=self._last_feedback,
        )

    def _build_observation_empty(self) -> PlannerObservation:
        """Build an empty observation for error states."""
        return PlannerObservation(
            project_id="none",
            project_name="No Active Project",
            project_description="No episode is active. Call reset() to start.",
            project_requirements=[],
            project_constraints=[],
            team_members=[],
            deadline_days=0,
            task_type="easy",
            task_instructions="Call reset() to begin.",
            feedback="No active episode.",
        )

    def _get_task_instructions(self, task_type: str) -> str:
        """Get specific instructions based on task difficulty."""
        instructions = {
            "easy": (
                "TASK: Break down the project into individual tasks.\n\n"
                "INSTRUCTIONS:\n"
                "1. Read the project description and requirements carefully.\n"
                "2. Identify all the individual tasks/subtasks needed to complete this project.\n"
                "3. Each task should be a concrete, actionable work item.\n"
                "4. Make sure your tasks cover ALL the requirements listed.\n\n"
                "SUBMIT your response as a list of tasks with names.\n"
                "Optional: include a category for each task (backend, frontend, testing, design, devops).\n\n"
                "You do NOT need to assign team members or estimate time for this task."
            ),
            "medium": (
                "TASK: Create a project plan with task breakdown, assignments, and estimates.\n\n"
                "INSTRUCTIONS:\n"
                "1. Break the project into individual tasks (cover ALL requirements).\n"
                "2. Assign each task to a team member based on their SKILLS.\n"
                "3. Estimate effort in working days for each task.\n"
                "4. Make sure no team member is assigned more work than their availability allows.\n"
                "   - Availability is given as a percentage of the deadline period.\n"
                "   - Example: Alice at 80% availability with 10 day deadline = 8 available days max.\n"
                "5. The total plan should fit within the deadline.\n\n"
                "SUBMIT your response with tasks including: name, assignee, and estimated_days.\n"
                "Optional: include priority and category."
            ),
            "hard": (
                "TASK: Create a COMPLETE sprint plan with full project management.\n\n"
                "INSTRUCTIONS:\n"
                "1. Break the project into individual tasks (cover ALL requirements).\n"
                "2. Assign each task to a team member based on their SKILLS and SENIORITY.\n"
                "3. Estimate effort in working days for each task.\n"
                "4. Set priority for each task (1 = highest priority, must be done first).\n"
                "5. Define dependencies between tasks (which tasks must be completed before others can start).\n"
                "6. Categorize each task (backend, frontend, testing, design, devops).\n"
                "7. Identify potential RISKS that could delay the project.\n"
                "8. Write a sprint SUMMARY describing the overall execution plan.\n\n"
                "CONSTRAINTS TO RESPECT:\n"
                "- Team members can only do tasks matching their skills.\n"
                "- Do not overload any team member beyond their available days.\n"
                "- Dependencies must not create circular chains.\n"
                "- The critical path (longest chain of dependencies) must fit in the deadline.\n"
                "- Consider seniority: assign complex tasks to senior members.\n\n"
                "SUBMIT your response with ALL fields: tasks (name, assignee, estimated_days, "
                "priority, depends_on, category), risks, and sprint_summary."
            ),
        }
        return instructions.get(task_type, instructions["easy"])

    def _grade_plan(self, action: PlannerAction) -> GraderResult:
        """
        Grade the agent's plan based on the current task type.
        Delegates to the appropriate grader.
        
        This method handles the core grading logic internally.
        For the hackathon, graders are also available as separate files.
        """
        task_type = self._current_task_type

        if task_type == "easy":
            return self._grade_easy(action)
        elif task_type == "medium":
            return self._grade_medium(action)
        elif task_type == "hard":
            return self._grade_hard(action)
        else:
            return GraderResult(
                score=0.0,
                feedback=f"Unknown task type: {task_type}",
            )

    # ══════════════════════════════════════════════════════
    #  GRADING LOGIC
    # ══════════════════════════════════════════════════════

    def _grade_easy(self, action: PlannerAction) -> GraderResult:
        """
        Grade EASY task: Task Breakdown
        
        Scoring:
        - Task coverage: Do the tasks cover the required features?
        - Bonus: Identifying non-obvious tasks (testing, documentation)
        - Penalty: Duplicate or irrelevant tasks
        """
        ground_truth = self._current_ground_truth
        required_tasks = ground_truth["required_tasks"]
        submitted_tasks = action.tasks

        # ── Validate basic submission ──────────────────────
        if not submitted_tasks or len(submitted_tasks) == 0:
            return GraderResult(
                score=0.0,
                breakdown={"task_coverage": 0.0},
                feedback="No tasks submitted. Please break the project into tasks.",
                penalties=["Empty submission: -100%"],
            )

        # ── Calculate task coverage ────────────────────────
        # For each required task, check if any submitted task matches
        matched_requirements = []
        unmatched_requirements = []

        for req_task in required_tasks:
            keyword = req_task["keyword"].lower()
            description = req_task["description"].lower()

            # Check if any submitted task matches this requirement
            found = False
            for sub_task in submitted_tasks:
                task_name = sub_task.name.lower()
                # Match by keyword presence in task name
                if (keyword in task_name or
                    any(word in task_name for word in description.split()
                        if len(word) > 3)):
                    found = True
                    break

            if found:
                matched_requirements.append(req_task["keyword"])
            else:
                unmatched_requirements.append(req_task["description"])

        # Coverage score
        coverage_score = len(matched_requirements) / len(required_tasks) if required_tasks else 0

        # ── Check for duplicates ───────────────────────────
        task_names = [t.name.lower().strip() for t in submitted_tasks]
        unique_names = set(task_names)
        duplicate_count = len(task_names) - len(unique_names)

        penalties = []
        penalty_amount = 0.0

        if duplicate_count > 0:
            penalty_amount += 0.05 * duplicate_count
            penalties.append(f"Duplicate tasks found ({duplicate_count}): -{duplicate_count * 5}%")

        # ── Check for reasonable number of tasks ───────────
        bonuses = []
        bonus_amount = 0.0

        if len(submitted_tasks) >= len(required_tasks):
            bonus_amount += 0.05
            bonuses.append("Comprehensive breakdown: +5%")

        # Check for bonus tasks (testing, documentation, etc.)
        bonus_keywords = ["test", "document", "review", "deploy", "monitor"]
        for sub_task in submitted_tasks:
            task_name = sub_task.name.lower()
            for keyword in bonus_keywords:
                if keyword in task_name:
                    bonus_amount += 0.02
                    bonuses.append(f"Identified '{keyword}' task: +2%")
                    break

        # Cap bonus
        bonus_amount = min(bonus_amount, 0.15)

        # ── Calculate final score ──────────────────────────
        final_score = max(0.0, min(1.0, coverage_score + bonus_amount - penalty_amount))

        # ── Build feedback ─────────────────────────────────
        feedback_parts = [
            f"Task Coverage: {len(matched_requirements)}/{len(required_tasks)} requirements covered ({coverage_score:.0%}).",
        ]

        if unmatched_requirements:
            feedback_parts.append(
                f"Missing: {', '.join(unmatched_requirements[:3])}."
            )

        if bonuses:
            feedback_parts.append(f"Bonuses: {', '.join(bonuses[:3])}.")

        if penalties:
            feedback_parts.append(f"Penalties: {', '.join(penalties)}.")

        feedback_parts.append(
            f"Final Score: {final_score:.2f}/1.00"
        )

        return GraderResult(
            score=round(final_score, 4),
            breakdown={
                "task_coverage": round(coverage_score, 4),
                "bonus": round(bonus_amount, 4),
                "penalty": round(penalty_amount, 4),
                "tasks_submitted": len(submitted_tasks),
                "requirements_matched": len(matched_requirements),
                "requirements_total": len(required_tasks),
            },
            feedback=" ".join(feedback_parts),
            penalties=penalties,
            bonuses=bonuses,
        )

    def _grade_medium(self, action: PlannerAction) -> GraderResult:
        """
        Grade MEDIUM task: Plan and Assign
        
        Scoring:
        - Task coverage (40%): Same as easy
        - Skill match (25%): Does assignee have required skills?
        - Availability (20%): Is anyone overloaded?
        - Deadline (15%): Does the plan fit in the deadline?
        """
        ground_truth = self._current_ground_truth
        required_tasks = ground_truth["required_tasks"]
        submitted_tasks = action.tasks
        team = self._current_team
        deadline = self._current_project["deadline_days"]

        # ── Validate basic submission ──────────────────────
        if not submitted_tasks or len(submitted_tasks) == 0:
            return GraderResult(
                score=0.0,
                breakdown={},
                feedback="No tasks submitted.",
                penalties=["Empty submission"],
            )

        # Build team member lookup
        team_lookup = {}
        for member in team["members"]:
            team_lookup[member["name"].lower()] = member

        penalties = []
        bonuses = []

        # ── 1. Task Coverage (40%) ─────────────────────────
        matched = 0
        unmatched = []
        for req_task in required_tasks:
            keyword = req_task["keyword"].lower()
            description = req_task["description"].lower()
            found = False
            for sub_task in submitted_tasks:
                task_name = sub_task.name.lower()
                if (keyword in task_name or
                    any(word in task_name for word in description.split()
                        if len(word) > 3)):
                    found = True
                    break
            if found:
                matched += 1
            else:
                unmatched.append(req_task["description"])

        coverage_score = matched / len(required_tasks) if required_tasks else 0

        # ── 2. Skill Match (25%) ───────────────────────────
        skill_matches = 0
        skill_mismatches = 0
        tasks_with_assignee = 0

        for sub_task in submitted_tasks:
            if sub_task.assignee:
                tasks_with_assignee += 1
                assignee_name = sub_task.assignee.lower()

                if assignee_name in team_lookup:
                    member = team_lookup[assignee_name]
                    member_skills = [s.lower() for s in member["skills"]]

                    # Check if task category matches member skills
                    task_name = sub_task.name.lower()
                    category = (sub_task.category or "").lower()

                    # Simple skill matching logic
                    has_relevant_skill = False

                    # Check category-based match
                    if category == "backend" and any(s in member_skills for s in
                        ["python", "django", "fastapi", "golang", "rest-api", "postgresql"]):
                        has_relevant_skill = True
                    elif category == "frontend" and any(s in member_skills for s in
                        ["javascript", "react", "html", "css", "typescript"]):
                        has_relevant_skill = True
                    elif category == "testing" and any(s in member_skills for s in
                        ["unit-testing", "integration-testing", "selenium", "manual-testing"]):
                        has_relevant_skill = True
                    elif category == "devops" and any(s in member_skills for s in
                        ["docker", "kubernetes", "ci-cd", "linux", "monitoring"]):
                        has_relevant_skill = True
                    elif category == "design" and any(s in member_skills for s in
                        ["figma", "css", "html", "responsive-design"]):
                        has_relevant_skill = True
                    else:
                        # Fallback: check if any task keyword matches any skill
                        task_words = task_name.split()
                        for word in task_words:
                            if word in member_skills:
                                has_relevant_skill = True
                                break

                    # If no category, be more lenient
                    if not category:
                        has_relevant_skill = True  # Give benefit of doubt

                    if has_relevant_skill:
                        skill_matches += 1
                    else:
                        skill_mismatches += 1
                        penalties.append(
                            f"Skill mismatch: {sub_task.assignee} may not have skills for '{sub_task.name}'"
                        )
                else:
                    skill_mismatches += 1
                    penalties.append(f"Unknown team member: {sub_task.assignee}")

        skill_score = skill_matches / tasks_with_assignee if tasks_with_assignee > 0 else 0

        # ── 3. Availability Check (20%) ────────────────────
        # Calculate total days assigned to each person
        member_load = {}
        for sub_task in submitted_tasks:
            if sub_task.assignee and sub_task.estimated_days:
                name = sub_task.assignee.lower()
                if name not in member_load:
                    member_load[name] = 0.0
                member_load[name] += sub_task.estimated_days

        overloaded_count = 0
        within_capacity_count = 0

        for name, total_days in member_load.items():
            if name in team_lookup:
                member = team_lookup[name]
                available_days = deadline * (member["availability_percent"] / 100.0)

                if total_days <= available_days:
                    within_capacity_count += 1
                else:
                    overloaded_count += 1
                    penalties.append(
                        f"Overloaded: {member['name']} assigned {total_days:.1f} days "
                        f"but only has {available_days:.1f} available"
                    )

        total_assigned = overloaded_count + within_capacity_count
        availability_score = within_capacity_count / total_assigned if total_assigned > 0 else 0

        # ── 4. Deadline Check (15%) ────────────────────────
        # Check if total estimated time is reasonable
        total_estimated = sum(
            t.estimated_days for t in submitted_tasks
            if t.estimated_days is not None
        )

        # Total team capacity
        total_capacity = sum(
            deadline * (m["availability_percent"] / 100.0)
            for m in team["members"]
        )

        if total_estimated <= total_capacity and total_estimated > 0:
            deadline_score = 1.0
            bonuses.append("Plan fits within team capacity")
        elif total_estimated > 0:
            deadline_score = max(0.0, total_capacity / total_estimated)
            penalties.append(
                f"Plan may exceed capacity: {total_estimated:.1f} days needed, "
                f"{total_capacity:.1f} days available"
            )
        else:
            deadline_score = 0.0
            penalties.append("No time estimates provided")

        # ── Calculate final score ──────────────────────────
        final_score = (
            coverage_score * 0.40 +
            skill_score * 0.25 +
            availability_score * 0.20 +
            deadline_score * 0.15
        )

        final_score = max(0.0, min(1.0, final_score))

        # ── Build feedback ─────────────────────────────────
        feedback = (
            f"Task Coverage: {matched}/{len(required_tasks)} ({coverage_score:.0%}). "
            f"Skill Match: {skill_matches}/{tasks_with_assignee} ({skill_score:.0%}). "
            f"Availability: {within_capacity_count}/{total_assigned} within capacity ({availability_score:.0%}). "
            f"Deadline: {'Feasible' if deadline_score >= 0.8 else 'Tight' if deadline_score >= 0.5 else 'Exceeds capacity'}. "
            f"Final Score: {final_score:.2f}/1.00."
        )

        if unmatched:
            feedback += f" Missing tasks: {', '.join(unmatched[:3])}."

        return GraderResult(
            score=round(final_score, 4),
            breakdown={
                "task_coverage": round(coverage_score, 4),
                "skill_match": round(skill_score, 4),
                "availability": round(availability_score, 4),
                "deadline_feasibility": round(deadline_score, 4),
                "tasks_submitted": len(submitted_tasks),
                "requirements_matched": matched,
                "requirements_total": len(required_tasks),
            },
            feedback=feedback,
            penalties=penalties[:5],  # Limit to 5 penalties
            bonuses=bonuses[:5],
        )

    def _grade_hard(self, action: PlannerAction) -> GraderResult:
        """
        Grade HARD task: Complete Sprint Plan
        
        Scoring:
        - Task coverage (25%): Requirements covered
        - Skill match (20%): Assignments match skills
        - Availability (15%): No one overloaded
        - Dependencies (15%): Correct task ordering
        - Risk identification (10%): Risks identified
        - Sprint summary (5%): Summary provided and meaningful
        - Deadline feasibility (10%): Plan fits in timeline
        """
        ground_truth = self._current_ground_truth
        required_tasks = ground_truth["required_tasks"]
        known_deps = ground_truth["known_dependencies"]
        known_risks = ground_truth["known_risks"]
        submitted_tasks = action.tasks
        team = self._current_team
        deadline = self._current_project["deadline_days"]

        # ── Validate basic submission ──────────────────────
        if not submitted_tasks or len(submitted_tasks) == 0:
            return GraderResult(
                score=0.0,
                breakdown={},
                feedback="No tasks submitted.",
                penalties=["Empty submission"],
            )

        team_lookup = {}
        for member in team["members"]:
            team_lookup[member["name"].lower()] = member

        penalties = []
        bonuses = []

        # ── 1. Task Coverage (25%) ─────────────────────────
        matched = 0
        for req_task in required_tasks:
            keyword = req_task["keyword"].lower()
            description = req_task["description"].lower()
            for sub_task in submitted_tasks:
                task_name = sub_task.name.lower()
                if (keyword in task_name or
                    any(word in task_name for word in description.split()
                        if len(word) > 3)):
                    matched += 1
                    break

        coverage_score = matched / len(required_tasks) if required_tasks else 0

        # ── 2. Skill Match (20%) ───────────────────────────
        skill_matches = 0
        tasks_with_assignee = 0

        for sub_task in submitted_tasks:
            if sub_task.assignee:
                tasks_with_assignee += 1
                assignee_name = sub_task.assignee.lower()

                if assignee_name in team_lookup:
                    member = team_lookup[assignee_name]
                    member_skills = [s.lower() for s in member["skills"]]
                    category = (sub_task.category or "").lower()

                    has_skill = False
                    if category == "backend" and any(s in member_skills for s in
                        ["python", "django", "fastapi", "golang", "rest-api", "postgresql"]):
                        has_skill = True
                    elif category == "frontend" and any(s in member_skills for s in
                        ["javascript", "react", "html", "css", "typescript"]):
                        has_skill = True
                    elif category == "testing" and any(s in member_skills for s in
                        ["unit-testing", "integration-testing", "selenium", "manual-testing"]):
                        has_skill = True
                    elif category == "devops" and any(s in member_skills for s in
                        ["docker", "kubernetes", "ci-cd", "linux", "monitoring"]):
                        has_skill = True
                    elif not category:
                        has_skill = True

                    if has_skill:
                        skill_matches += 1
                    else:
                        penalties.append(f"Skill mismatch: {sub_task.assignee} for '{sub_task.name}'")
                else:
                    penalties.append(f"Unknown team member: {sub_task.assignee}")

        skill_score = skill_matches / tasks_with_assignee if tasks_with_assignee > 0 else 0

        # ── 3. Availability (15%) ──────────────────────────
        member_load = {}
        for sub_task in submitted_tasks:
            if sub_task.assignee and sub_task.estimated_days:
                name = sub_task.assignee.lower()
                member_load[name] = member_load.get(name, 0.0) + sub_task.estimated_days

        overloaded = 0
        within_capacity = 0
        for name, total_days in member_load.items():
            if name in team_lookup:
                member = team_lookup[name]
                available = deadline * (member["availability_percent"] / 100.0)
                if total_days <= available:
                    within_capacity += 1
                else:
                    overloaded += 1
                    penalties.append(f"Overloaded: {member['name']}")

        total_assigned = overloaded + within_capacity
        availability_score = within_capacity / total_assigned if total_assigned > 0 else 0

        # ── 4. Dependencies (15%) ──────────────────────────
        # Check if agent identified key dependencies
        submitted_deps = set()
        for sub_task in submitted_tasks:
            if sub_task.depends_on:
                for dep in sub_task.depends_on:
                    submitted_deps.add(dep.lower())

        # Check for circular dependencies
        has_circular = self._check_circular_dependencies(submitted_tasks)
        if has_circular:
            penalties.append("Circular dependency detected!")

        # Check against known dependencies
        dep_matches = 0
        for known_dep in known_deps:
            dep_task = known_dep["depends_on"].lower()
            if any(dep_task in d for d in submitted_deps):
                dep_matches += 1

        dep_score = dep_matches / len(known_deps) if known_deps else 0
        if has_circular:
            dep_score *= 0.5  # Halve score for circular deps

        # Bonus if agent has any dependencies at all
        if submitted_deps and not has_circular:
            bonuses.append("Dependencies defined correctly")

        # ── 5. Risk Identification (10%) ───────────────────
        submitted_risks = action.risks or []

        risk_matches = 0
        if submitted_risks:
            for known_risk in known_risks:
                risk_lower = known_risk.lower()
                risk_keywords = [w for w in risk_lower.split() if len(w) > 3]
                for sub_risk in submitted_risks:
                    sub_lower = sub_risk.lower()
                    if any(kw in sub_lower for kw in risk_keywords):
                        risk_matches += 1
                        break

        risk_score = risk_matches / len(known_risks) if known_risks else 0

        # Bonus for identifying any risks
        if submitted_risks:
            bonus_risk = min(len(submitted_risks) * 0.1, 0.3)
            risk_score = min(1.0, risk_score + bonus_risk)
            bonuses.append(f"Identified {len(submitted_risks)} risks")

        # ── 6. Sprint Summary (5%) ─────────────────────────
        summary = action.sprint_summary or ""
        if len(summary) > 50:
            summary_score = 1.0
            bonuses.append("Detailed sprint summary provided")
        elif len(summary) > 20:
            summary_score = 0.5
        else:
            summary_score = 0.0
            if not summary:
                penalties.append("No sprint summary provided")

        # ── 7. Deadline Feasibility (10%) ──────────────────
        total_estimated = sum(
            t.estimated_days for t in submitted_tasks
            if t.estimated_days is not None
        )
        total_capacity = sum(
            deadline * (m["availability_percent"] / 100.0)
            for m in team["members"]
        )

        if total_estimated <= total_capacity and total_estimated > 0:
            deadline_score = 1.0
        elif total_estimated > 0:
            deadline_score = max(0.0, total_capacity / total_estimated)
        else:
            deadline_score = 0.0

        # ── Calculate final score ──────────────────────────
        final_score = (
            coverage_score * 0.25 +
            skill_score * 0.20 +
            availability_score * 0.15 +
            dep_score * 0.15 +
            risk_score * 0.10 +
            summary_score * 0.05 +
            deadline_score * 0.10
        )

        final_score = max(0.0, min(1.0, final_score))

        # ── Build feedback ─────────────────────────────────
        feedback = (
            f"Coverage: {matched}/{len(required_tasks)} ({coverage_score:.0%}). "
            f"Skills: {skill_score:.0%}. "
            f"Availability: {availability_score:.0%}. "
            f"Dependencies: {dep_score:.0%}. "
            f"Risks: {risk_score:.0%}. "
            f"Summary: {'✓' if summary_score > 0 else '✗'}. "
            f"Deadline: {'OK' if deadline_score >= 0.8 else 'Tight'}. "
            f"Final: {final_score:.2f}/1.00."
        )

        return GraderResult(
            score=round(final_score, 4),
            breakdown={
                "task_coverage": round(coverage_score, 4),
                "skill_match": round(skill_score, 4),
                "availability": round(availability_score, 4),
                "dependencies": round(dep_score, 4),
                "risk_identification": round(risk_score, 4),
                "sprint_summary": round(summary_score, 4),
                "deadline_feasibility": round(deadline_score, 4),
            },
            feedback=feedback,
            penalties=penalties[:5],
            bonuses=bonuses[:5],
        )

    def _check_circular_dependencies(self, tasks: list) -> bool:
        """
        Check if the task dependencies form a circular chain.
        Uses simple DFS-based cycle detection.
        
        Returns True if circular dependency found.
        """
        # Build adjacency list
        task_names = {t.name.lower(): t for t in tasks}
        graph = {}

        for task in tasks:
            name = task.name.lower()
            graph[name] = []
            if task.depends_on:
                for dep in task.depends_on:
                    graph[name].append(dep.lower())

        # DFS cycle detection
        visited = set()
        in_stack = set()

        def has_cycle(node):
            if node in in_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            in_stack.add(node)

            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True

            in_stack.remove(node)
            return False

        for node in graph:
            if has_cycle(node):
                return True

        return False