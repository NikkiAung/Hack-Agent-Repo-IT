from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import asyncio
from github_service import GitHubService, GitHubAnalyzer
from gemini_service import GeminiService

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
github_service = GitHubService()
gemini_service = GeminiService()

# Pydantic models
class Chapter(BaseModel):
    id: int
    title: str
    description: str
    tasks: List[str]
    tips: List[str]
    next_steps: str

class LearningPath(BaseModel):
    overall_progress: int
    chapters: List[Chapter]

class RepoAnalysisRequest(BaseModel):
    repo_url: str
    role: str

class RepoAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    role: str
    repository: str
    insights: dict
    summary: str

class OnboardingPlanRequest(BaseModel):
    repo_url: str
    role: str

class CodeTourRequest(BaseModel):
    repo_url: str
    role: str

class RecommendIssuesRequest(BaseModel):
    repo_url: str
    role: str
    experience_level: str

class OnboardingProgressRequest(BaseModel):
    user_id: str
    event: str
    details: dict = {}

# In-memory learning path data
learning_path = LearningPath(
    overall_progress=0,
    chapters=[
        Chapter(
            id=1,
            title="Welcome & Repo Overview",
            description="Get oriented with the org's frontend repo, its purpose, and high-level architecture.",
            tasks=[
                "Walk through the README and key directories",
                "Identify the main framework (e.g. React / Vue / Angular) and folder structure",
                "Map out where core features live (components, services, assets)"
            ],
            tips=[
                "Start by reading the README.md file",
                "Look at package.json to identify dependencies",
                "Check the src directory structure"
            ],
            next_steps="After understanding the repo structure, proceed to setting up your local environment."
        ),
        Chapter(
            id=2,
            title="Local Setup & Tooling",
            description="Install dependencies, configure linters/formatters, and run the app locally.",
            tasks=[
                "Install Node.js, package manager (npm / yarn / pnpm)",
                "Configure .env files for API endpoints",
                "Run npm install � npm start and explore live-reload",
                "Set up ESLint, Prettier, TypeScript (if used), and Husky for pre-commit checks"
            ],
            tips=[
                "Check for .env.example files to guide configuration",
                "Use the recommended Node.js version in .nvmrc if available",
                "Pay attention to any setup scripts in package.json"
            ],
            next_steps="Once your local environment is set up, dive into the architecture and code structure."
        ),
        Chapter(
            id=3,
            title="Architecture & Code Structure",
            description="Deep dive into how the code is organized and how modules interact.",
            tasks=[
                "Explain \"feature-based\" vs \"layered\" directory patterns",
                "Show how UI, state, and API layers are separated",
                "Diagram component hierarchy and data flow"
            ],
            tips=[
                "Look for architecture documentation in the wiki or docs folder",
                "Trace a feature from UI to API to understand the patterns",
                "Identify global state management approaches"
            ],
            next_steps="After understanding the architecture, explore the UI components and design system."
        ),
        Chapter(
            id=4,
            title="UI Components & Design System",
            description="Learn the reusable component library, theming tokens, and best practices.",
            tasks=[
                "Browse the components/ui folder: Cards, Buttons, Inputs, etc.",
                "Use the Storybook (or equivalent) to interact with components",
                "Build a new \"HelloWorld\" component and style it with the design tokens"
            ],
            tips=[
                "Look for a design system or UI kit documentation",
                "Check for theme files that define colors, spacing, and typography",
                "Study how existing components implement responsive design"
            ],
            next_steps="With a good understanding of the UI components, move on to how state is managed."
        ),
        Chapter(
            id=5,
            title="State Management & Data Flow",
            description="Understand how global and local state are handled.",
            tasks=[
                "Introduce Redux / Vuex / Pinia / Context API patterns",
                "Trace an example action � reducer � state � UI update",
                "Add a new slice of state (e.g. \"notifications\") and wire it into a component"
            ],
            tips=[
                "Look for store configuration files",
                "Follow a user interaction from component to state update",
                "Note how asynchronous state changes are handled"
            ],
            next_steps="Now that you understand state management, learn how the app connects to backend services."
        ),
        Chapter(
            id=6,
            title="API Integration & Services",
            description="Hook up to backend endpoints via REST or GraphQL services.",
            tasks=[
                "Review the services/api.ts (or similar) abstraction layer",
                "Fetch data from one endpoint, display it in a component",
                "Handle loading, success, and error states"
            ],
            tips=[
                "Look for API client configuration",
                "Study how authentication tokens are managed",
                "Note how error handling is standardized"
            ],
            next_steps="After understanding API integration, explore how navigation is handled."
        ),
        Chapter(
            id=7,
            title="Routing & Navigation",
            description="Configure client-side routing and protected routes.",
            tasks=[
                "Set up React Router / Vue Router with nested routes",
                "Implement a \"Login � Dashboard � Settings\" flow",
                "Guard routes behind authentication state"
            ],
            tips=[
                "Find the router configuration file",
                "Study how protected routes are implemented",
                "Note how route parameters are used"
            ],
            next_steps="With routing understood, explore how styles and theming are handled."
        ),
        Chapter(
            id=8,
            title="Styling & Theming",
            description="Apply CSS-in-JS, Tailwind, Sass or plain CSS methodologies.",
            tasks=[
                "Customize theme tokens (colors, spacing, fonts)",
                "Create a dark-mode toggle using CSS variables",
                "Optimize critical-path CSS for performance"
            ],
            tips=[
                "Identify the styling approach (CSS modules, styled components, etc.)",
                "Look for theme configuration files",
                "Study how responsive design is implemented"
            ],
            next_steps="After mastering styling, learn about testing practices."
        ),
        Chapter(
            id=9,
            title="Testing & Quality Assurance",
            description="Write unit, integration, and end-to-end tests for frontend code.",
            tasks=[
                "Configure Jest + React Testing Library or Cypress",
                "Write a snapshot test for a button component",
                "Automate a login-logout E2E test"
            ],
            tips=[
                "Check for test configuration files",
                "Study existing tests for patterns",
                "Look for testing utilities and mocks"
            ],
            next_steps="With testing knowledge, learn how the app is built and deployed."
        ),
        Chapter(
            id=10,
            title="Build, Deployment & CI/CD",
            description="Learn how the app is built, packaged, and deployed.",
            tasks=[
                "Run npm run build and inspect the /dist folder",
                "Configure a GitHub Actions workflow for lint � test � deploy",
                "Verify a deployment on staging and production"
            ],
            tips=[
                "Check build scripts in package.json",
                "Look for CI configuration files",
                "Study environment-specific configurations"
            ],
            next_steps="Next, learn about contributing guidelines and best practices."
        ),
        Chapter(
            id=11,
            title="Contributing & Best Practices",
            description="Guidelines for code style, feature branches, PR reviews, and issue tracking.",
            tasks=[
                "How to pick up a ticket, branch naming, commit messages",
                "PR template walkthrough and required CI checks",
                "How to request reviews, resolve comments, and merge safely"
            ],
            tips=[
                "Look for CONTRIBUTING.md or similar docs",
                "Review recent PRs for examples",
                "Note code review practices"
            ],
            next_steps="Finally, explore advanced patterns for optimization and extensibility."
        ),
        Chapter(
            id=12,
            title="Advanced Patterns & Extensibility",
            description="Explore performance optimizations, plugin systems, and future-proofing.",
            tasks=[
                "Code-splitting and lazy loading strategies",
                "How to extend the design system or add new plugins",
                "Profiling with browser devtools and lighthouse"
            ],
            tips=[
                "Look for code-splitting implementations",
                "Study how extensibility is built into the architecture",
                "Review performance optimization techniques"
            ],
            next_steps="You've completed all chapters! Apply what you've learned by contributing to the codebase."
        )
    ]
)

# In-memory progress store (for hackathon/demo)
onboarding_progress_store = {}

# API Endpoints
@app.get("/api/learning-path")
async def get_learning_path():
    return learning_path

@app.post("/api/analyze-repository")
async def analyze_repository(request: RepoAnalysisRequest):
    """
    Analyze a GitHub repository and return role-specific insights using real GitHub API and Gemini AI
    """
    try:
        # Extract owner and repo name from URL
        if "github.com" not in request.repo_url:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        
        url_parts = request.repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
        if len(url_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format")
        
        owner, repo = url_parts[0], url_parts[1]
        role = request.role
        username = None
        # Optionally extract username from request or repo data for developer role
        # (For demo, use repo owner as username if not provided)
        if role == "developer":
            username = owner
        # Fetch role-specific insights
        if role == "developer":
            insights = await github_service.get_developer_insights(owner, repo, username)
        elif role == "em":
            insights = await github_service.get_em_insights(owner, repo)
        elif role == "tpm":
            insights = await github_service.get_tpm_insights(owner, repo)
        elif role == "pm":
            insights = await github_service.get_pm_insights(owner, repo)
        elif role == "qa":
            insights = await github_service.get_qa_insights(owner, repo)
        elif role == "scrum":
            insights = await github_service.get_scrum_insights(owner, repo)
        elif role == "ux":
            insights = await github_service.get_ux_insights(owner, repo)
        elif role == "executive":
            insights = await github_service.get_executive_insights(owner, repo)
        else:
            insights = {}
        # Generate AI-powered summary using Gemini
        summary = ""
        try:
            ai_summary = await gemini_service.generate_role_insights(role, insights, owner, repo)
            summary = ai_summary.get("summary", "")
        except Exception as e:
            summary = f"AI summary unavailable: {e}"
        response = {
            "success": True,
            "role": role,
            "repository": request.repo_url,
            "insights": insights,
            "summary": summary
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/onboarding-plan")
async def onboarding_plan(request: OnboardingPlanRequest):
    """
    Generate a personalized onboarding plan for a new contributor based on repo structure, issues, and docs.
    """
    try:
        # Extract owner and repo name from URL
        if "github.com" not in request.repo_url:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        url_parts = request.repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
        if len(url_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format")
        owner, repo = url_parts[0], url_parts[1]

        # Fetch repo file tree
        github_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        headers = github_service.headers
        import requests as pyrequests
        tree_resp = pyrequests.get(github_api_url, headers=headers)
        tree = tree_resp.json().get('tree', []) if tree_resp.status_code == 200 else []

        # Fetch open issues (good first issue/help wanted)
        issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        issues_params = {"state": "open", "labels": "good first issue,help wanted", "per_page": 20}
        issues_resp = pyrequests.get(issues_url, headers=headers, params=issues_params)
        issues = issues_resp.json() if issues_resp.status_code == 200 else []

        # Fetch docs (README, CONTRIBUTING, etc.)
        docs_files = [f for f in tree if f['type'] == 'blob' and f['path'].lower() in ["readme.md", "contributing.md", "docs/readme.md"]]
        docs_content = {}
        for doc in docs_files:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{doc['path']}"
            doc_resp = pyrequests.get(raw_url)
            if doc_resp.status_code == 200:
                docs_content[doc['path']] = doc_resp.text[:2000]  # Limit for prompt

        # Prepare summary for Gemini
        file_tree_str = "\n".join(f['path'] for f in tree[:30])
        issues_str = "\n".join(f"- {i['title']} ({i['html_url']})" for i in issues)
        docs_str = "\n".join(f"{k}: {v[:200]}..." for k, v in docs_content.items())
        summary = f"""
Repo file tree (top 30):
{file_tree_str}

Open issues (good first/help wanted):
{issues_str}

Docs:
{docs_str}
"""
        prompt = f"""
You are an onboarding assistant for a GitHub repository. Given the following repo structure, open issues, and docs, generate a step-by-step onboarding plan for a new {request.role}.

{summary}

The plan should include:
- Which files/folders to start with (and why)
- Which open issues to tackle first (with links)
- Which docs to read (with links)
- Any other tips for onboarding as a {request.role}
Respond in JSON with fields: steps (list of step objects with title, description, url if relevant), tips (list), and summary (string).
"""
        # Use Gemini to generate the plan
        plan = await gemini_service.generate_onboarding_plan(prompt)
        return {"plan": plan}
    except Exception as e:
        print(f"Onboarding plan error: {e}")
        raise HTTPException(status_code=500, detail=f"Onboarding plan failed: {str(e)}")

@app.post("/api/code-tour")
async def code_tour(request: CodeTourRequest):
    """
    Generate an interactive code walkthrough for a repo using Gemini.
    """
    try:
        if "github.com" not in request.repo_url:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        url_parts = request.repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
        if len(url_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format")
        owner, repo = url_parts[0], url_parts[1]
        # Fetch repo file tree
        github_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        headers = github_service.headers
        import requests as pyrequests
        tree_resp = pyrequests.get(github_api_url, headers=headers)
        tree = tree_resp.json().get('tree', []) if tree_resp.status_code == 200 else []
        # Fetch docs (README, etc.)
        docs_files = [f for f in tree if f['type'] == 'blob' and f['path'].lower() in ["readme.md", "docs/readme.md"]]
        docs_content = {}
        for doc in docs_files:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{doc['path']}"
            doc_resp = pyrequests.get(raw_url)
            if doc_resp.status_code == 200:
                docs_content[doc['path']] = doc_resp.text[:2000]
        # Prepare summary for Gemini
        file_tree_str = "\n".join(f['path'] for f in tree[:30])
        docs_str = "\n".join(f"{k}: {v[:200]}..." for k, v in docs_content.items())
        summary = f"""
Repo file tree (top 30):\n{file_tree_str}\n\nDocs:\n{docs_str}\n"""
        prompt = f"""
You are a code tour assistant for a GitHub repository. Given the following repo structure and docs, generate a step-by-step code walkthrough for a new {request.role}.\n\n{summary}\n\nFor each step, include: title, description, file/line, code snippet, and why it matters. Respond in JSON as a list of steps."""
        steps = await gemini_service.generate_code_tour(prompt)
        return {"steps": steps}
    except Exception as e:
        print(f"Code tour error: {e}")
        raise HTTPException(status_code=500, detail=f"Code tour failed: {str(e)}")

@app.post("/api/recommend-issues")
async def recommend_issues(request: RecommendIssuesRequest):
    """
    Recommend issues/tasks for a user based on repo, role, and experience.
    """
    try:
        if "github.com" not in request.repo_url:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        url_parts = request.repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
        if len(url_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format")
        owner, repo = url_parts[0], url_parts[1]
        # Fetch open issues
        issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        headers = github_service.headers
        import requests as pyrequests
        issues_resp = pyrequests.get(issues_url, headers=headers, params={"state": "open", "per_page": 50})
        issues = issues_resp.json() if issues_resp.status_code == 200 else []
        # Prepare summary for Gemini
        issues_str = "\n".join(f"- {i['title']} ({i['html_url']})" for i in issues[:20])
        prompt = f"""
You are an onboarding agent. Given the following open issues for {owner}/{repo}, recommend 3-5 issues or tasks that are best suited for a new {request.role} with {request.experience_level} experience.\n\nOpen issues:\n{issues_str}\n\nRespond in JSON as a list of recommendations, each with title, description, and url."""
        recommendations = await gemini_service.generate_issue_recommendations(prompt)
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"Recommend issues error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommend issues failed: {str(e)}")

@app.post("/api/onboarding-progress")
async def onboarding_progress(request: OnboardingProgressRequest):
    """
    Track and return onboarding progress, badges, and streaks for a user.
    """
    user_id = request.user_id
    event = request.event
    details = request.details
    if user_id not in onboarding_progress_store:
        onboarding_progress_store[user_id] = {
            "completed_steps": set(),
            "badges": set(),
            "streak": 0,
            "level": 1,
            "last_event": None
        }
    user_data = onboarding_progress_store[user_id]
    # Update progress
    if event == "completed_step":
        step_id = details.get("step_id")
        if step_id:
            user_data["completed_steps"].add(step_id)
    elif event == "first_pr":
        user_data["badges"].add("First PR")
    elif event == "first_review":
        user_data["badges"].add("First Review")
    elif event == "quiz_passed":
        user_data["badges"].add("Quiz Master")
    # Streak logic (simple: +1 per event per day)
    import datetime
    now = datetime.datetime.utcnow().date()
    if user_data["last_event"] != now:
        user_data["streak"] += 1
        user_data["last_event"] = now
    # Level up logic
    if len(user_data["completed_steps"]) >= 5:
        user_data["level"] = 2
    if len(user_data["completed_steps"]) >= 10:
        user_data["level"] = 3
    return {
        "completed_steps": list(user_data["completed_steps"]),
        "badges": list(user_data["badges"]),
        "streak": user_data["streak"],
        "level": user_data["level"]
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)