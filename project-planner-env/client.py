import requests
from typing import Optional
from models import PlannerAction, PlannerObservation, PlannerState, StepResult


class PlannerClient:
    """
    HTTP client for ProjectPlannerEnv.
    
    Connects to the FastAPI server and provides the 3-method interface:
    reset(), step(), state()
    
    Example:
        client = PlannerClient(base_url="http://localhost:8000")
        
        # Start easy task
        result = client.reset(task_type="easy")
        print(result.observation.project_description)
        
        # Submit a plan
        from models import PlannerAction, TaskItem
        action = PlannerAction(tasks=[
            TaskItem(name="Design database"),
            TaskItem(name="Build API"),
        ])
        result = client.step(action)
        print(f"Score: {result.reward}")
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Args:
            base_url: URL of the environment server.
                     Local: "http://localhost:8000"
                     HF Space: "https://username-project-planner-env.hf.space"
        """
        self.base_url = base_url.rstrip("/")
        self._verify_connection()

    def _verify_connection(self):
        """Check if the server is reachable."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connected to {data.get('environment', 'Unknown')} "
                      f"v{data.get('version', '?')}")
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
        except requests.ConnectionError:
            print(f"⚠️ Could not connect to {self.base_url}. "
                  f"Make sure the server is running.")

    def health(self) -> dict:
        """Check server health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def reset(self, task_type: str = "easy",
              project_id: Optional[str] = None) -> StepResult:
        """
        Start a new episode.
        
        Args:
            task_type: "easy", "medium", or "hard"
            project_id: Optional specific project ID
            
        Returns:
            StepResult with initial observation
        """
        payload = {"task_type": task_type}
        if project_id:
            payload["project_id"] = project_id

        response = requests.post(
            f"{self.base_url}/reset",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return StepResult(**data)

    def step(self, action: PlannerAction) -> StepResult:
        """
        Submit a project plan and get graded.
        
        Args:
            action: PlannerAction with tasks, risks, sprint_summary
            
        Returns:
            StepResult with reward and feedback
        """
        payload = {"action": action.model_dump()}
        response = requests.post(
            f"{self.base_url}/step",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return StepResult(**data)

    def state(self) -> PlannerState:
        """
        Get current episode metadata.
        
        Returns:
            PlannerState with episode info
        """
        response = requests.get(
            f"{self.base_url}/state",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return PlannerState(**data)

    def get_tasks(self) -> dict:
        """Get available task definitions."""
        response = requests.get(f"{self.base_url}/tasks", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_projects(self) -> dict:
        """Get available project scenarios."""
        response = requests.get(f"{self.base_url}/projects", timeout=10)
        response.raise_for_status()
        return response.json()

    def run_grader(self, task_type: str, project_id: str,
                   action: PlannerAction) -> dict:
        """Run grader independently."""
        payload = {
            "task_type": task_type,
            "project_id": project_id,
            "action": action.model_dump(),
        }
        response = requests.post(
            f"{self.base_url}/grader",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()