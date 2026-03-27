import json
import requests

BASE_URL = "http://localhost:8000"


def get_plan_for_difficulty(difficulty):
    """Return a hardcoded plan optimized for each difficulty level."""

    if difficulty == "easy":
        return {
            "action": {
                "tasks": [
                    {"name": "Design homepage layout", "assignee": "Bob", "estimated_days": 2, "priority": 1, "depends_on": [], "category": "design"},
                    {"name": "Build responsive HTML/CSS structure", "assignee": "Alice", "estimated_days": 3, "priority": 1, "depends_on": ["Design homepage layout"], "category": "frontend"},
                    {"name": "Create portfolio gallery component", "assignee": "Alice", "estimated_days": 2, "priority": 2, "depends_on": ["Build responsive HTML/CSS structure"], "category": "frontend"},
                    {"name": "Build contact form with validation", "assignee": "Alice", "estimated_days": 2, "priority": 2, "depends_on": ["Build responsive HTML/CSS structure"], "category": "frontend"},
                    {"name": "Add SEO meta tags and accessibility", "assignee": "Bob", "estimated_days": 1, "priority": 3, "depends_on": ["Design homepage layout"], "category": "design"},
                    {"name": "Cross-browser testing and QA", "assignee": "Bob", "estimated_days": 2, "priority": 3, "depends_on": ["Create portfolio gallery component", "Build contact form with validation"], "category": "testing"},
                ],
                "risks": [
                    "Design iterations may delay frontend development if requirements are unclear",
                    "Cross-browser compatibility issues could require extra responsive fixes",
                    "Contact form email delivery may fail without proper SMTP configuration"
                ],
                "sprint_summary": "Week 1: Bob designs the layout while Alice builds the HTML/CSS foundation. Week 2: Alice builds the gallery and contact form in parallel. Bob handles SEO, accessibility audit, and final QA testing."
            }
        }

    elif difficulty == "medium":
        return {
            "action": {
                "tasks": [
                    {"name": "Design database schema for products and users", "assignee": "Alice", "estimated_days": 2, "priority": 1, "depends_on": [], "category": "backend"},
                    {"name": "Implement user authentication with email verification", "assignee": "Alice", "estimated_days": 3, "priority": 1, "depends_on": ["Design database schema for products and users"], "category": "backend"},
                    {"name": "Build product listing API with search and filter", "assignee": "Charlie", "estimated_days": 3, "priority": 1, "depends_on": ["Design database schema for products and users"], "category": "backend"},
                    {"name": "Create React product listing UI with filters", "assignee": "Bob", "estimated_days": 3, "priority": 2, "depends_on": ["Build product listing API with search and filter"], "category": "frontend"},
                    {"name": "Implement shopping cart frontend and backend", "assignee": "Bob", "estimated_days": 3, "priority": 2, "depends_on": ["Create React product listing UI with filters"], "category": "frontend"},
                    {"name": "Integrate Stripe payment processing", "assignee": "Alice", "estimated_days": 3, "priority": 1, "depends_on": ["Implement shopping cart frontend and backend"], "category": "backend"},
                    {"name": "Build order management and confirmation emails", "assignee": "Charlie", "estimated_days": 2, "priority": 2, "depends_on": ["Integrate Stripe payment processing"], "category": "backend"},
                    {"name": "Create admin dashboard for products and orders", "assignee": "Charlie", "estimated_days": 3, "priority": 3, "depends_on": ["Build order management and confirmation emails"], "category": "frontend"},
                    {"name": "Build seller profile and ratings system", "assignee": "Bob", "estimated_days": 2, "priority": 3, "depends_on": ["Implement user authentication with email verification"], "category": "frontend"},
                    {"name": "Implement inventory tracking and stock management", "assignee": "Alice", "estimated_days": 2, "priority": 2, "depends_on": ["Design database schema for products and users"], "category": "backend"},
                    {"name": "Write API and integration tests", "assignee": "Diana", "estimated_days": 4, "priority": 2, "depends_on": ["Build product listing API with search and filter", "Integrate Stripe payment processing"], "category": "testing"},
                    {"name": "Security audit and performance testing", "assignee": "Diana", "estimated_days": 3, "priority": 3, "depends_on": ["Write API and integration tests"], "category": "testing"},
                ],
                "risks": [
                    "Stripe API integration complexity may cause delays in payment flow",
                    "PCI DSS compliance requirements could require architecture changes",
                    "Database performance under concurrent load needs early optimization",
                    "Email delivery service reliability affects user verification flow",
                    "Cross-team dependency on database schema could create bottleneck"
                ],
                "sprint_summary": "Sprint 1 (Week 1-2): Alice designs DB schema and builds auth. Charlie builds product API. Bob starts frontend after API is ready. Sprint 2 (Week 3-4): Payment integration, cart, and order flow. Diana begins testing. Sprint 3 (Week 5): Admin dashboard, seller profiles, inventory, security audit and performance testing."
            }
        }

    else:  # hard
        return {
            "action": {
                "tasks": [
                    {"name": "Design multi-tenant database architecture", "assignee": "Alice", "estimated_days": 3, "priority": 1, "depends_on": [], "category": "backend"},
                    {"name": "Set up Kubernetes cluster with auto-scaling", "assignee": "Diana", "estimated_days": 3, "priority": 1, "depends_on": [], "category": "devops"},
                    {"name": "Implement WebSocket real-time messaging layer", "assignee": "Alice", "estimated_days": 4, "priority": 1, "depends_on": ["Design multi-tenant database architecture"], "category": "backend"},
                    {"name": "Build Kanban board with drag-and-drop UI", "assignee": "Bob", "estimated_days": 4, "priority": 1, "depends_on": ["Implement WebSocket real-time messaging layer"], "category": "frontend"},
                    {"name": "Create Gantt chart with dependency visualization", "assignee": "Bob", "estimated_days": 4, "priority": 2, "depends_on": ["Build Kanban board with drag-and-drop UI"], "category": "frontend"},
                    {"name": "Implement RBAC and SSO with SAML/OAuth", "assignee": "Charlie", "estimated_days": 4, "priority": 1, "depends_on": ["Design multi-tenant database architecture"], "category": "backend"},
                    {"name": "Build real-time chat with encryption", "assignee": "Eve", "estimated_days": 4, "priority": 2, "depends_on": ["Implement WebSocket real-time messaging layer"], "category": "backend"},
                    {"name": "Implement file upload with version history", "assignee": "Charlie", "estimated_days": 3, "priority": 2, "depends_on": ["Implement RBAC and SSO with SAML/OAuth"], "category": "backend"},
                    {"name": "Build time tracking module with timer", "assignee": "Eve", "estimated_days": 3, "priority": 3, "depends_on": ["Build Kanban board with drag-and-drop UI"], "category": "frontend"},
                    {"name": "Create automated reporting engine with charts", "assignee": "Charlie", "estimated_days": 3, "priority": 3, "depends_on": ["Build time tracking module with timer"], "category": "backend"},
                    {"name": "Build REST API with OpenAPI docs and webhooks", "assignee": "Alice", "estimated_days": 3, "priority": 2, "depends_on": ["Implement RBAC and SSO with SAML/OAuth"], "category": "backend"},
                    {"name": "Implement full-text search across all entities", "assignee": "Eve", "estimated_days": 2, "priority": 3, "depends_on": ["Design multi-tenant database architecture"], "category": "backend"},
                    {"name": "Build notification system with email and in-app", "assignee": "Charlie", "estimated_days": 2, "priority": 3, "depends_on": ["Implement WebSocket real-time messaging layer"], "category": "backend"},
                    {"name": "Create PWA with offline task viewing", "assignee": "Bob", "estimated_days": 3, "priority": 3, "depends_on": ["Build Kanban board with drag-and-drop UI"], "category": "frontend"},
                    {"name": "Set up CI/CD pipeline with zero-downtime deploy", "assignee": "Diana", "estimated_days": 3, "priority": 2, "depends_on": ["Set up Kubernetes cluster with auto-scaling"], "category": "devops"},
                    {"name": "Implement monitoring, logging, and alerting", "assignee": "Diana", "estimated_days": 3, "priority": 2, "depends_on": ["Set up CI/CD pipeline with zero-downtime deploy"], "category": "devops"},
                    {"name": "Build audit log for SOC2 compliance", "assignee": "Alice", "estimated_days": 2, "priority": 2, "depends_on": ["Implement RBAC and SSO with SAML/OAuth"], "category": "backend"},
                    {"name": "Implement data export in CSV, PDF, JSON", "assignee": "Eve", "estimated_days": 2, "priority": 4, "depends_on": ["Create automated reporting engine with charts"], "category": "backend"},
                    {"name": "Database migration strategy planning", "assignee": "Alice", "estimated_days": 2, "priority": 2, "depends_on": ["Design multi-tenant database architecture"], "category": "research"},
                    {"name": "Security penetration testing and OWASP audit", "assignee": "Frank", "estimated_days": 4, "priority": 1, "depends_on": ["Implement RBAC and SSO with SAML/OAuth", "Build real-time chat with encryption"], "category": "testing"},
                    {"name": "Load testing for 10k concurrent WebSocket connections", "assignee": "Frank", "estimated_days": 3, "priority": 2, "depends_on": ["Implement WebSocket real-time messaging layer", "Set up Kubernetes cluster with auto-scaling"], "category": "testing"},
                    {"name": "End-to-end integration test suite", "assignee": "Frank", "estimated_days": 4, "priority": 2, "depends_on": ["Security penetration testing and OWASP audit"], "category": "testing"},
                    {"name": "WCAG AAA accessibility audit and fixes", "assignee": "Bob", "estimated_days": 2, "priority": 3, "depends_on": ["Create PWA with offline task viewing"], "category": "design"},
                ],
                "risks": [
                    "WebSocket scaling to 10k concurrent connections requires extensive load testing and may need architecture revision",
                    "Multi-tenant data isolation bugs could cause catastrophic data leaks between organizations",
                    "SSO integration with SAML 2.0 has complex edge cases across identity providers",
                    "Real-time Gantt chart rendering with large dependency graphs may cause browser performance issues",
                    "SOC 2 and GDPR compliance requirements may surface unexpected architectural constraints late in development",
                    "End-to-end encryption for chat adds complexity to search and backup features",
                    "Zero-downtime database migrations with multi-tenant schema changes are extremely risky",
                    "Team bandwidth split across 6 people with heavy cross-dependencies creates coordination overhead"
                ],
                "sprint_summary": "Phase 1 (Week 1-2): Alice designs DB architecture, Diana sets up K8s and CI/CD, Charlie starts auth/RBAC. Phase 2 (Week 3-4): Alice builds WebSocket layer, Bob starts Kanban UI, Eve builds chat. Phase 3 (Week 5-6): Gantt charts, file uploads, time tracking, reporting, API+webhooks. Frank begins security testing. Phase 4 (Week 7): Search, notifications, PWA, data export, compliance audit. Phase 5 (Week 8-9): Load testing, integration tests, accessibility audit, performance optimization, final QA."
            }
        }


def run_single_baseline(difficulty):
    """Run baseline on a single difficulty and return the score."""
    print(f"\n{'='*50}")
    print(f"Running baseline for: {difficulty.upper()}")
    print(f"{'='*50}")

    # Reset
    reset_resp = requests.post(f"{BASE_URL}/reset", json={
        "task_type": difficulty,
        "project_id": None
    })
    print(f"Reset response: {reset_resp.status_code}")

    if reset_resp.status_code != 200:
        print(f"Reset failed: {reset_resp.text}")
        return {"score": 0.0, "difficulty": difficulty, "error": "Reset failed"}

    # Get plan
    plan = get_plan_for_difficulty(difficulty)

    # Step
    step_resp = requests.post(f"{BASE_URL}/step", json=plan)
    print(f"Step response: {step_resp.status_code}")

    if step_resp.status_code != 200:
        print(f"Step failed: {step_resp.text}")
        return {"score": 0.0, "difficulty": difficulty, "error": "Step failed"}

    result = step_resp.json()
    print(f"Result: {json.dumps(result, indent=2)}")

    # Extract score from result
    score = 0.0
    if "reward" in result:
        score = result["reward"]
    elif "score" in result:
        score = result["score"]
    elif "info" in result and "score" in result["info"]:
        score = result["info"]["score"]

    return {
        "score": round(float(score), 4),
        "difficulty": difficulty,
        "full_result": result
    }


def run_all_baselines():
    """Run baseline inference on all 3 difficulties. Returns dict of results."""
    results = {}
    for difficulty in ["easy", "medium", "hard"]:
        result = run_single_baseline(difficulty)
        results[difficulty] = {
            "score": result["score"],
            "difficulty": difficulty
        }
        if "error" in result:
            results[difficulty]["error"] = result["error"]

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPlannerEnv — Baseline Inference")
    print("=" * 60)

    results = run_all_baselines()

    print("\n" + "=" * 60)
    print("BASELINE RESULTS SUMMARY")
    print("=" * 60)

    total = 0.0
    for diff in ["easy", "medium", "hard"]:
        r = results[diff]
        score = r["score"]
        total += score
        status = "✅" if score > 0.5 else "⚠️" if score > 0.2 else "❌"
        print(f"  {diff.upper():8s}: {score:.4f} {status}")

    avg = total / 3
    print(f"\n  AVERAGE : {avg:.4f}")
    print("=" * 60)
