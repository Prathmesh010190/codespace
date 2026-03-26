from pydantic import BaseModel, Field
from typing import List, Optional


class TeamMember(BaseModel):
    """
    Represents one team member available for the project.
    
    Example:
        TeamMember(
            name="Alice",
            role="Senior Backend Developer",
            skills=["python", "django", "postgresql"],
            experience_years=7,
            availability_percent=80,
            seniority="senior"
        )
    """
    name: str = Field(
        description="Team member's name"
    )
    role: str = Field(
        description="Job title, e.g. 'Senior Backend Developer'"
    )
    skills: List[str] = Field(
        description="List of technical skills, e.g. ['python', 'django']"
    )
    experience_years: int = Field(
        description="Years of experience"
    )
    availability_percent: int = Field(
        description="How available they are (0-100). 80 means 80% available."
    )
    seniority: str = Field(
        description="Seniority level: 'junior', 'mid', or 'senior'"
    )


class TaskItem(BaseModel):
    """
    Represents one task in the project plan created by the agent.
    
    Example:
        TaskItem(
            name="Implement OAuth backend",
            assignee="Alice",
            estimated_days=3.0,
            priority=1,
            depends_on=["Design OAuth flow"],
            category="backend"
        )
    """
    name: str = Field(
        description="Short name of the task"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Name of team member assigned. None for easy task."
    )
    estimated_days: Optional[float] = Field(
        default=None,
        description="Estimated days to complete. None for easy task."
    )
    priority: Optional[int] = Field(
        default=None,
        description="Priority order (1 = highest). None for easy task."
    )
    depends_on: Optional[List[str]] = Field(
        default=None,
        description="List of task names this depends on. None for easy task."
    )
    category: Optional[str] = Field(
        default=None,
        description="Category: 'backend', 'frontend', 'testing', 'design', 'devops'"
    )



class PlannerObservation(BaseModel):
    """
    What the agent SEES when it connects to the environment.
    This is returned by reset() and step().
    
    Contains:
    - The project to plan
    - The team available
    - The deadline
    - Which task difficulty to solve
    - Feedback from the grader (after step)
    """
    project_id: str = Field(
        description="Unique identifier for this project scenario"
    )
    project_name: str = Field(
        description="Short name of the project"
    )
    project_description: str = Field(
        description="Detailed description of what needs to be built"
    )
    project_requirements: List[str] = Field(
        description="List of specific features/requirements that must be covered"
    )
    project_constraints: List[str] = Field(
        description="Technical or business constraints, e.g. 'Must use OAuth 2.0'"
    )
    team_members: List[TeamMember] = Field(
        description="Available team members with their skills and availability"
    )
    deadline_days: int = Field(
        description="Number of working days until deadline"
    )
    task_type: str = Field(
        description="Difficulty level: 'easy', 'medium', or 'hard'"
    )
    task_instructions: str = Field(
        description="Specific instructions for this task difficulty level"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Feedback from grader after a step. None on first observation."
    )


class PlannerAction(BaseModel):
    """
    What the agent SENDS as its project plan.
    This is the input to step().
    
    For easy task: Only 'tasks' with names is required.
    For medium task: tasks + assignee + estimated_days required.
    For hard task: Everything required including risks and summary.
    """
    tasks: List[TaskItem] = Field(
        description="List of planned tasks for the project"
    )
    risks: Optional[List[str]] = Field(
        default=None,
        description="Identified risks. Required for hard task."
    )
    sprint_summary: Optional[str] = Field(
        default=None,
        description="Overall sprint plan summary. Required for hard task."
    )


class PlannerState(BaseModel):
    """
    Episode metadata returned by state().
    Contains information about the current episode.
    """
    episode_id: str = Field(
        description="Unique identifier for this episode"
    )
    step_count: int = Field(
        description="Number of steps taken in this episode"
    )
    max_steps: int = Field(
        default=3,
        description="Maximum steps allowed per episode"
    )
    current_task: str = Field(
        description="Current task difficulty: 'easy', 'medium', or 'hard'"
    )
    project_id: str = Field(
        description="Which project scenario is being used"
    )
    is_done: bool = Field(
        default=False,
        description="Whether the episode is finished"
    )
    current_reward: float = Field(
        default=0.0,
        description="Cumulative reward for this episode"
    )


class StepResult(BaseModel):
    """
    The complete result returned by step() and reset().
    Bundles observation + reward + done flag + extra info.
    """
    observation: PlannerObservation = Field(
        description="What the agent sees"
    )
    reward: float = Field(
        default=0.0,
        description="Reward for this step"
    )
    done: bool = Field(
        default=False,
        description="Whether the episode is over"
    )
    info: dict = Field(
        default_factory=dict,
        description="Extra information (grader scores, breakdown, etc.)"
    )


class GraderResult(BaseModel):
    """
    Result from a grader after evaluating the agent's plan.
    Score is always between 0.0 and 1.0.
    """
    score: float = Field(
        description="Overall score from 0.0 (worst) to 1.0 (perfect)"
    )
    breakdown: dict = Field(
        default_factory=dict,
        description="Detailed score breakdown by category"
    )
    feedback: str = Field(
        default="",
        description="Human-readable feedback explaining the score"
    )
    penalties: List[str] = Field(
        default_factory=list,
        description="List of penalties applied"
    )
    bonuses: List[str] = Field(
        default_factory=list,
        description="List of bonuses awarded"
    )