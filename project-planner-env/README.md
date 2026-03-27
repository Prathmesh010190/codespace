---
title: ProjectPlannerEnv
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
tags:
  - openenv
---

# ProjectPlannerEnv

AI Project Manager OpenEnv environment. Plan projects, assign tasks, estimate effort, identify risks.

## Endpoints
- POST /reset - Start episode
- POST /step - Submit plan
- GET /state - Current state
- GET /tasks - Available tasks
- GET /grader - Last score
- POST /baseline - Run all baselines
