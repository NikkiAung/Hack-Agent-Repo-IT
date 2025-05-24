import os
import requests
import json
import base64
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API keys
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Task(BaseModel):
    description: str
    completed: bool = False

class Tip(BaseModel):
    content: str

class Chapter(BaseModel):
    id: int
    title: str
    description: str
    tasks: List[str]
    tips: List[str]
    next_steps: str
    quiz_questions: Optional[List[Dict[str, Any]]] = None

class LearningPath(BaseModel):
    overall_progress: int
    chapters: List[Chapter]
    repo_name: str
    repo_description: str
    repo_url: str
    onboarding_summary: Dict[str, Any]

class GitHubRepoRequest(BaseModel):
    repo_url: str
    user_experience_level: str = "beginner"
    focus_areas: List[str] = []

class TestResult(BaseModel):
    chapter_id: int
    questions: List[Dict[str, Any]]
    score: int
    feedback: str

# GitHub API helper functions
def get_repo_info(repo_url: str) -> tuple:
    """Extract owner and repo name from a GitHub URL"""
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def github_request(url: str) -> Dict[str, Any]:
    """Make a GitHub API request with proper headers"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"GitHub API error: {response.json().get('message', 'Unknown error')}"
        )
    
    return response.json()

def fetch_repo_data(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch comprehensive repository data for onboarding"""
    # Basic repo information
    repo_info = github_request(f"https://api.github.com/repos/{owner}/{repo}")
    
    # Root contents to analyze project structure
    contents = github_request(f"https://api.github.com/repos/{owner}/{repo}/contents")
    
    # Languages used in the repo
    languages = github_request(f"https://api.github.com/repos/{owner}/{repo}/languages")
    
    # README content if available
    readme_content = ""
    for item in contents:
        if item["name"].lower() == "readme.md":
            readme_response = requests.get(item["download_url"])
            if readme_response.status_code == 200:
                readme_content = readme_response.text
            break
    
    # Get branches
    branches = github_request(f"https://api.github.com/repos/{owner}/{repo}/branches")
    
    # Get workflow files if they exist
    workflows = []
    try:
        workflow_contents = github_request(f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows")
        workflows = workflow_contents
    except:
        # If no workflows directory, just continue
        pass
    
    # Get labels for issue tracking
    labels = github_request(f"https://api.github.com/repos/{owner}/{repo}/labels")
    
    # Check for test directories
    test_dirs = []
    test_patterns = ["tests", "test", "__tests__", "spec", "cypress"]
    for item in contents:
        if item["type"] == "dir" and any(pattern in item["name"].lower() for pattern in test_patterns):
            test_dirs.append(item)
    
    # Look for linters and config files
    linters = []
    config_files = []
    linter_patterns = [
        ".eslintrc", ".prettierrc", ".stylelintrc", "pylintrc", ".flake8",
        "setup.cfg", "tslint", "rubocop", ".editorconfig", ".gitlab-ci.yml"
    ]
    config_patterns = [
        ".env.example", "config.example", "docker-compose", "Dockerfile",
        "package.json", "requirements.txt", "Pipfile", "pom.xml"
    ]
    
    for item in contents:
        if item["type"] == "file":
            filename = item["name"].lower()
            if any(pattern in filename for pattern in linter_patterns):
                linters.append(item)
            if any(pattern in filename for pattern in config_patterns):
                config_files.append(item)
    
    # Get docs directory if it exists
    docs = []
    try:
        docs_contents = github_request(f"https://api.github.com/repos/{owner}/{repo}/contents/docs")
        docs = docs_contents
    except:
        # If no docs directory, just continue
        pass
    
    # Get .github directory for contributing guidelines
    contributing = {}
    try:
        github_contents = github_request(f"https://api.github.com/repos/{owner}/{repo}/contents/.github")
        for item in github_contents:
            if item["name"].lower() in ["contributing.md", "pull_request_template.md", "issue_template.md"]:
                file_response = requests.get(item["download_url"])
                if file_response.status_code == 200:
                    contributing[item["name"]] = file_response.text
    except:
        # If no .github directory, just continue
        pass
    
    # Structure all the data
    return {
        "repo_info": repo_info,
        "readme": readme_content,
        "languages": languages,
        "branches": branches,
        "workflows": workflows,
        "labels": labels,
        "test_directories": test_dirs,
        "linters": linters,
        "config_files": config_files,
        "docs": docs,
        "contributing": contributing
    }

def analyze_onboarding_data(repo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze repository data to extract onboarding information"""
    summary = {
        "environment_tooling": {
            "languages": list(repo_data["languages"].keys()),
            "config_files": [item["name"] for item in repo_data["config_files"]],
            "setup_required": True if repo_data["config_files"] else False
        },
        "git_workflow": {
            "default_branch": repo_data["repo_info"]["default_branch"],
            "branches": [branch["name"] for branch in repo_data["branches"]],
            "protected_branches": [branch["name"] for branch in repo_data["branches"] if branch.get("protected", False)]
        },
        "code_style": {
            "linters": [item["name"] for item in repo_data["linters"]],
            "has_formatting_rules": True if repo_data["linters"] else False
        },
        "documentation": {
            "has_readme": True if repo_data["readme"] else False,
            "has_docs_folder": True if repo_data["docs"] else False,
            "contributing_guidelines": list(repo_data["contributing"].keys())
        },
        "testing": {
            "test_directories": [item["name"] for item in repo_data["test_directories"]]
        },
        "ci_cd": {
            "workflows": [item["name"] for item in repo_data["workflows"]]
        },
        "issue_tracking": {
            "labels": [item["name"] for item in repo_data["labels"]]
        }
    }
    
    return summary

def generate_onboarding_path(repo_data: Dict[str, Any], onboarding_summary: Dict[str, Any], experience_level: str) -> Dict[str, Any]:
    """Generate an onboarding learning path using Gemini"""
    model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
    
    # Create prompt for Gemini
    prompt = f"""
    You are an expert onboarding agent for software developers. Generate an onboarding learning path for a {experience_level} developer
    who is joining a team working on the following GitHub repository:
    
    Repository: {repo_data["repo_info"]["name"]}
    Description: {repo_data["repo_info"]["description"] or "No description provided"}
    Primary languages: {", ".join(list(repo_data["languages"].keys())[:3])}
    
    Based on my analysis, here are key aspects of this repository:
    
    Environment & Tooling:
    - Languages: {", ".join(onboarding_summary["environment_tooling"]["languages"])}
    - Configuration files: {", ".join(onboarding_summary["environment_tooling"]["config_files"])}
    
    Git Workflow:
    - Default branch: {onboarding_summary["git_workflow"]["default_branch"]}
    - Protected branches: {", ".join(onboarding_summary["git_workflow"]["protected_branches"])}
    
    Code Style:
    - Linters/formatters: {", ".join(onboarding_summary["code_style"]["linters"])}
    
    Testing:
    - Test directories: {", ".join(onboarding_summary["testing"]["test_directories"])}
    
    CI/CD:
    - Workflow files: {", ".join(onboarding_summary["ci_cd"]["workflows"])}
    
    Documentation:
    - Has README: {onboarding_summary["documentation"]["has_readme"]}
    - Has docs folder: {onboarding_summary["documentation"]["has_docs_folder"]}
    - Contributing guidelines: {", ".join(onboarding_summary["documentation"]["contributing_guidelines"])}
    
    Create an 8-chapter onboarding learning path that covers the following areas:
    
    Chapter 1: Repository Overview & Setup
    Chapter 2: Environment & Tooling
    Chapter 3: Git Workflow & Branching
    Chapter 4: Code Style & Linters
    Chapter 5: Documentation & Architecture
    Chapter 6: Testing Strategy
    Chapter 7: CI/CD & Deployment
    Chapter 8: Contributing Guidelines & Best Practices
    
    For each chapter include:
    1. A clear title
    2. A concise description
    3. 3-5 specific tasks to complete
    4. 2-3 helpful tips
    5. Next steps after completing the chapter
    6. 2 quiz questions (with multiple choices and correct answers) to test understanding
    
    Format the response as a JSON object following this structure:
    {{
      "chapters": [
        {{
          "id": 1,
          "title": "Chapter Title",
          "description": "Chapter description",
          "tasks": ["Task 1", "Task 2", "Task 3"],
          "tips": ["Tip 1", "Tip 2"],
          "next_steps": "Next steps description",
          "quiz_questions": [
            {{
              "question": "What is the correct way to do X?",
              "choices": ["Option A", "Option B", "Option C", "Option D"],
              "correct_answer": "Option B",
              "explanation": "Option B is correct because..."
            }},
            {{
              "question": "Question 2 text here?",
              "choices": ["Option A", "Option B", "Option C", "Option D"],
              "correct_answer": "Option C",
              "explanation": "Option C is correct because..."
            }}
          ]
        }},
        ...more chapters...
      ]
    }}
    """
    
    response = model.generate_content(prompt)
    
    try:
        # Extract JSON from response
        json_text = response.text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
            
        learning_path_data = json.loads(json_text)
        return learning_path_data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        # If parsing fails, generate a fallback response
        return generate_fallback_chapters()

def generate_fallback_chapters():
    """Generate fallback chapters if AI generation fails"""
    return {
        "chapters": [
            {
                "id": 1,
                "title": "Repository Overview & Setup",
                "description": "Get familiar with the repository structure and set up your local environment",
                "tasks": [
                    "Clone the repository locally", 
                    "Install required dependencies",
                    "Run the application locally"
                ],
                "tips": [
                    "Read the README.md file thoroughly",
                    "Check for any .env.example files to set up your environment"
                ],
                "next_steps": "Once your environment is set up, move on to understanding the tools used",
                "quiz_questions": [
                    {
                        "question": "What is the first file you should check when starting with a new repository?",
                        "choices": ["package.json", "README.md", "index.js", ".gitignore"],
                        "correct_answer": "README.md",
                        "explanation": "README.md contains essential information about the project, its purpose, and setup instructions."
                    },
                    {
                        "question": "What command is typically used to install dependencies in a JavaScript project?",
                        "choices": ["npm start", "npm install", "npm build", "npm run"],
                        "correct_answer": "npm install",
                        "explanation": "npm install is used to install all dependencies listed in package.json."
                    }
                ]
            },
            {
                "id": 2,
                "title": "Environment & Tooling",
                "description": "Learn about the development tools and environment configuration",
                "tasks": [
                    "Identify the package manager (npm, yarn, etc.)",
                    "Configure your IDE with recommended extensions",
                    "Set up environment variables"
                ],
                "tips": [
                    "Check package.json for scripts and dependencies",
                    "Look for .editorconfig or IDE configuration files"
                ],
                "next_steps": "After configuring your environment, learn about the Git workflow",
                "quiz_questions": [
                    {
                        "question": "Why is it important to use the same package manager as the rest of the team?",
                        "choices": ["It's not important", "To maintain lock file consistency", "To use fewer disk space", "To write better code"],
                        "correct_answer": "To maintain lock file consistency",
                        "explanation": "Using the same package manager ensures lockfiles (package-lock.json, yarn.lock) remain consistent across the team."
                    },
                    {
                        "question": "What file typically contains environment variables examples?",
                        "choices": [".env", ".env.example", ".gitignore", "config.js"],
                        "correct_answer": ".env.example",
                        "explanation": ".env.example provides a template of required environment variables without actual values."
                    }
                ]
            },
            # Chapters 3-8 would be similarly structured
        ]
    }

def evaluate_user_knowledge(chapter_id: int, user_answers: List[Dict]) -> TestResult:
    """Evaluate user's answers to quiz questions"""
    # In a real implementation, this would fetch the correct chapter
    # and compare user's answers with correct answers
    
    # For demo purposes, create a mock result
    questions = [
        {
            "question": "What is the correct Git command to create a new branch?",
            "choices": [
                "git branch new-branch", 
                "git checkout -b new-branch", 
                "git create new-branch", 
                "git new-branch"
            ],
            "correct_answer": "git checkout -b new-branch",
            "explanation": "git checkout -b creates and immediately switches to the new branch",
            "user_answer": user_answers[0]["answer"]
        },
        {
            "question": "When should you rebase your branch?",
            "choices": [
                "Always before pushing to remote", 
                "Only when there are conflicts", 
                "Before creating a pull request if the base branch has new commits", 
                "Never, always use merge"
            ],
            "correct_answer": "Before creating a pull request if the base branch has new commits",
            "explanation": "Rebasing keeps the history cleaner when the base branch has progressed since you created your branch",
            "user_answer": user_answers[1]["answer"]
        }
    ]
    
    # Calculate score
    correct_count = 0
    for i, q in enumerate(questions):
        if user_answers[i]["answer"] == q["correct_answer"]:
            correct_count += 1
    
    score = int((correct_count / len(questions)) * 100)
    
    # Generate feedback based on score
    if score >= 80:
        feedback = "Great job! You have a solid understanding of this chapter's material."
    elif score >= 50:
        feedback = "Good effort. Review the areas where you made mistakes to strengthen your understanding."
    else:
        feedback = "You may need to review this chapter again. Focus on the explanations for the questions you missed."
    
    return TestResult(
        chapter_id=chapter_id,
        questions=questions,
        score=score,
        feedback=feedback
    )

# API endpoints
@app.post("/api/generate-onboarding-path")
async def create_onboarding_path(
    request: GitHubRepoRequest,
    background_tasks: BackgroundTasks,
):
    """Generate an onboarding learning path from a GitHub repository"""
    try:
        # Parse repo URL
        owner, repo = get_repo_info(request.repo_url)
        
        # Fetch repository data
        repo_data = fetch_repo_data(owner, repo)
        
        # Analyze repository data for onboarding
        onboarding_summary = analyze_onboarding_data(repo_data)
        
        # Generate learning path
        learning_path_data = generate_onboarding_path(
            repo_data,
            onboarding_summary,
            request.user_experience_level
        )
        
        # Create response
        return LearningPath(
            overall_progress=0,  # Start with 0 progress
            chapters=learning_path_data["chapters"],
            repo_name=repo_data["repo_info"]["name"],
            repo_description=repo_data["repo_info"]["description"] or "No description provided",
            repo_url=request.repo_url,
            onboarding_summary=onboarding_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-knowledge/{chapter_id}")
async def test_chapter_knowledge(
    chapter_id: int,
    user_answers: List[Dict],
):
    """Test user's understanding of a specific chapter"""
    try:
        # Evaluate user's answers
        result = evaluate_user_knowledge(chapter_id, user_answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repo-structure/{owner}/{repo}")
async def get_repo_structure(owner: str, repo: str):
    """Get repository structure for visualization"""
    try:
        contents = github_request(f"https://api.github.com/repos/{owner}/{repo}/contents")
        
        # Process into a tree structure
        structure = []
        for item in contents:
            if item["type"] == "dir":
                # For directories, we might want to fetch their contents too
                structure.append({
                    "name": item["name"],
                    "path": item["path"],
                    "type": "dir",
                    "url": item["url"]
                })
            else:
                structure.append({
                    "name": item["name"],
                    "path": item["path"],
                    "type": "file",
                    "size": item["size"],
                    "url": item["download_url"]
                })
        
        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-content/{owner}/{repo}/{file_path:path}")
async def get_file_content(owner: str, repo: str, file_path: str):
    """Get content of a specific file"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        content_data = github_request(url)
        
        if content_data.get("encoding") == "base64":
            content = base64.b64decode(content_data["content"]).decode('utf-8')
            return {"content": content}
        
        return {"error": "File content not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)