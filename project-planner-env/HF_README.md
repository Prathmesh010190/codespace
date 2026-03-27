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

# 🎯 ProjectPlannerEnv — OpenEnv Environment

AI Project Manager environment where an agent reads project briefs, breaks them into tasks, assigns team members, estimates effort, and identifies risks.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /reset | POST | Start new episode |
| /step | POST | Submit project plan |
| /state | GET | Get current state |
| /tasks | GET | List available tasks |
| /grader | GET | Get last score |
| /baseline | POST | Run all baselines |
| /health | GET | Health check |

## Baseline Scores

| Difficulty | Score |
|-----------|-------|
| Easy | 0.395 |
| Medium | 0.35 |
| Hard | 0.45 |
| Average | 0.398 |
