from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import json
from pathlib import Path

# Create the app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define models
class Chapter(BaseModel):
    id: int
    title: str
    description: str
    tasks: List[str]
    tips: List[str]
    next_steps: str
    quiz_questions: Optional[List[dict]] = None

class LearningPath(BaseModel):
    overall_progress: int
    chapters: List[Chapter]
    repo_name: Optional[str] = None
    repo_description: Optional[str] = None

# Helper functions
def get_repo_info(repo_url: str):
    # Extract owner and repo name from URL
    # Format: https://github.com/owner/repo
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def fetch_repo_data(repo_url: str):
    owner, repo = get_repo_info(repo_url)
    
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    # Basic repo info
    try:
        repo_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers
        )
        
        if repo_response.status_code != 200:
            error_msg = repo_response.json().get('message', 'Unknown error')
            return {"error": f"GitHub API error: {error_msg}"}
        
        repo_data = repo_response.json()
        
        # Get languages
        languages_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            headers=headers
        )
        
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        return {
            "repo_info": {
                "name": repo_data["name"],
                "description": repo_data["description"],
                "default_branch": repo_data["default_branch"],
                "language": repo_data["language"],
                "url": repo_data["html_url"]
            },
            "languages": languages,
            "success": True
        }
    
    except Exception as e:
        return {"error": f"Error accessing GitHub API: {str(e)}"}

def generate_learning_path(repo_data):
    """
    Generate a simple learning path based on repository data
    """
    # Get primary language
    primary_language = repo_data["repo_info"]["language"] or "Unknown"
    languages = list(repo_data["languages"].keys())
    
    # Generate a simple learning path with 8 chapters
    chapters = [
        Chapter(
            id=1,
            title="Repository Overview & Setup",
            description=f"Get familiar with the {repo_data['repo_info']['name']} repository and set up your local environment.",
            tasks=[
                "Clone the repository locally",
                "Read the README.md file",
                "Identify the main components and features"
            ],
            tips=[
                "Pay special attention to any setup instructions in the README",
                "Look for .env.example files to configure your environment"
            ],
            next_steps="Once your environment is set up, explore the codebase structure.",
            quiz_questions=[
                {
                    "question": "What is the main programming language used in this repository?",
                    "choices": [
                        primary_language,
                        "Java",
                        "C++",
                        "Ruby"
                    ],
                    "correct_answer": primary_language
                },
                {
                    "question": "What is the default branch for this repository?",
                    "choices": [
                        repo_data["repo_info"]["default_branch"],
                        "develop",
                        "staging",
                        "production"
                    ],
                    "correct_answer": repo_data["repo_info"]["default_branch"]
                }
            ]
        ),
        Chapter(
            id=2,
            title="Code Structure & Architecture",
            description=f"Understand how the codebase is organized and how different components interact.",
            tasks=[
                "Map out the directory structure",
                "Identify key modules and their responsibilities",
                "Trace the flow of a typical request or operation"
            ],
            tips=[
                "Draw a diagram of the main components",
                "Look for design patterns in the code"
            ],
            next_steps="After understanding the code structure, learn about the development workflow.",
            quiz_questions=[
                {
                    "question": "What architectural pattern is likely used in this codebase?",
                    "choices": [
                        "Model-View-Controller (MVC)",
                        "Microservices",
                        "Monolithic",
                        "Event-driven"
                    ],
                    "correct_answer": "Model-View-Controller (MVC)"
                }
            ]
        ),
        Chapter(
            id=3,
            title="Development Workflow",
            description="Learn the Git workflow and development process used by the team.",
            tasks=[
                f"Create a feature branch from {repo_data['repo_info']['default_branch']}",
                "Make a small change and commit it",
                "Open a pull request"
            ],
            tips=[
                "Follow the team's branch naming convention",
                "Write clear commit messages"
            ],
            next_steps="Once comfortable with the workflow, learn about testing practices.",
            quiz_questions=[
                {
                    "question": "What is the recommended approach for merging changes?",
                    "choices": [
                        "Pull Request",
                        "Direct push to main",
                        "Cherry-pick commits",
                        "Merge without review"
                    ],
                    "correct_answer": "Pull Request"
                }
            ]
        ),
        Chapter(
            id=4,
            title="Testing Practices",
            description="Understand the testing strategy and how to write tests.",
            tasks=[
                "Run the existing test suite",
                "Identify different types of tests (unit, integration, etc.)",
                "Write a simple test for your feature"
            ],
            tips=[
                "Check for testing frameworks in package.json or requirements files",
                "Look for test examples in the codebase"
            ],
            next_steps="After understanding testing, explore the deployment process.",
            quiz_questions=[
                {
                    "question": "Why is testing important in software development?",
                    "choices": [
                        "To ensure code quality and prevent regressions",
                        "It's just a formality",
                        "Only for catching syntax errors",
                        "It's not important for small projects"
                    ],
                    "correct_answer": "To ensure code quality and prevent regressions"
                }
            ]
        )
    ]
    
    # Add more language-specific chapters if we know the language
    if primary_language in ["JavaScript", "TypeScript"]:
        chapters.append(
            Chapter(
                id=5,
                title=f"{primary_language} Best Practices",
                description=f"Learn the best practices for writing {primary_language} code in this project.",
                tasks=[
                    "Review the ESLint or TSLint configuration",
                    "Understand the project's module system",
                    "Learn how async operations are handled"
                ],
                tips=[
                    "Look for patterns in how Promise/async-await is used",
                    "Check for utility functions that are commonly used"
                ],
                next_steps="Next, explore the frontend framework and components.",
                quiz_questions=[
                    {
                        "question": f"What is a common pattern for handling asynchronous operations in {primary_language}?",
                        "choices": [
                            "async/await",
                            "goto statements",
                            "global variables",
                            "recursive functions"
                        ],
                        "correct_answer": "async/await"
                    }
                ]
            )
        )
    elif primary_language == "Python":
        chapters.append(
            Chapter(
                id=5,
                title="Python Best Practices",
                description="Learn the best practices for writing Python code in this project.",
                tasks=[
                    "Review any linter configurations (pylint, flake8, etc.)",
                    "Understand the project's module system",
                    "Learn how the project handles dependencies"
                ],
                tips=[
                    "Look for virtual environment setup instructions",
                    "Check for utility functions and helpers"
                ],
                next_steps="Next, explore the backend framework and API structure.",
                quiz_questions=[
                    {
                        "question": "What is a common tool for managing Python dependencies?",
                        "choices": [
                            "pip and requirements.txt",
                            "npm",
                            "gradle",
                            "make"
                        ],
                        "correct_answer": "pip and requirements.txt"
                    }
                ]
            )
        )
    
    # Create the learning path
    return LearningPath(
        overall_progress=0,
        chapters=chapters,
        repo_name=repo_data["repo_info"]["name"],
        repo_description=repo_data["repo_info"]["description"] or "No description provided"
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse(
        "form.html", 
        {"request": request, "repo_url": "", "experience_level": "beginner", "error": None, "result": None}
    )

@app.post("/", response_class=HTMLResponse)
async def analyze_repo(request: Request, repo_url: str = Form(...), experience_level: str = Form(...)):
    try:
        # Fetch repository data
        repo_data = fetch_repo_data(repo_url)
        
        if "error" in repo_data:
            return templates.TemplateResponse(
                "form.html", 
                {
                    "request": request, 
                    "repo_url": repo_url, 
                    "experience_level": experience_level, 
                    "error": repo_data["error"],
                    "result": None,
                    "result_json": None
                }
            )
        
        # Generate learning path
        learning_path = generate_learning_path(repo_data)
        
        # Convert to JSON for display
        result_json = json.dumps(learning_path.dict(), indent=2)
        
        return templates.TemplateResponse(
            "form.html", 
            {
                "request": request, 
                "repo_url": repo_url, 
                "experience_level": experience_level,
                "error": None,
                "result": learning_path,
                "result_json": result_json
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "form.html", 
            {
                "request": request, 
                "repo_url": repo_url, 
                "experience_level": experience_level,
                "error": f"An error occurred: {str(e)}",
                "result": None,
                "result_json": None
            }
        )

@app.post("/api/generate-learning-path")
async def api_generate_learning_path(repo_url: str, experience_level: str = "beginner"):
    try:
        repo_data = fetch_repo_data(repo_url)
        
        if "error" in repo_data:
            raise HTTPException(status_code=400, detail=repo_data["error"])
        
        learning_path = generate_learning_path(repo_data)
        return learning_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-path")
async def get_learning_path():
    # Return a sample learning path
    return LearningPath(
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
                    "Run npm install → npm start and explore live-reload",
                    "Set up ESLint, Prettier, TypeScript (if used), and Husky for pre-commit checks"
                ],
                tips=[
                    "Check for .env.example files to guide configuration",
                    "Use the recommended Node.js version in .nvmrc if available",
                    "Pay attention to any setup scripts in package.json"
                ],
                next_steps="Once your local environment is set up, dive into the architecture and code structure."
            )
        ],
        repo_name="Sample Repo",
        repo_description="A sample repository for demonstration"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)