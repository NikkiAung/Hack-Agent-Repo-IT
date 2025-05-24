import os
import requests
import json
from typing import List, Dict, Any
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends, Header
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
    repo_name: str
    repo_description: str

class GitHubRepoRequest(BaseModel):
    repo_url: str
    user_experience_level: str = "beginner"
    focus_areas: List[str] = []
    
# GitHub API functions
def get_github_repo_data(repo_url: str) -> Dict[str, Any]:
    """
    Fetch repository data from GitHub API
    
    Args:
        repo_url: URL of the GitHub repository
    
    Returns:
        Dict containing repository data
    """
    # Extract owner and repo name from URL
    # Format: https://github.com/owner/repo
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    # Get repository info
    repo_response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}", 
        headers=headers
    )
    
    if repo_response.status_code != 200:
        raise HTTPException(status_code=repo_response.status_code, 
                           detail=f"GitHub API error: {repo_response.json().get('message', 'Unknown error')}")
    
    repo_data = repo_response.json()
    
    # Get repository contents
    contents_response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents", 
        headers=headers
    )
    
    if contents_response.status_code != 200:
        raise HTTPException(status_code=contents_response.status_code, 
                           detail=f"GitHub API error: {contents_response.json().get('message', 'Unknown error')}")
    
    contents_data = contents_response.json()
    
    # Get README content if available
    readme_content = ""
    for item in contents_data:
        if item["name"].lower() == "readme.md":
            readme_response = requests.get(item["download_url"])
            if readme_response.status_code == 200:
                readme_content = readme_response.text
            break
    
    # Get languages used
    languages_response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/languages", 
        headers=headers
    )
    
    languages_data = {}
    if languages_response.status_code == 200:
        languages_data = languages_response.json()
    
    # Combine all data
    return {
        "repo_info": repo_data,
        "contents": contents_data,
        "readme": readme_content,
        "languages": languages_data
    }

def get_repo_structure(repo_url: str, depth: int = 2) -> Dict[str, Any]:
    """
    Get repository file structure up to specified depth
    
    Args:
        repo_url: URL of the GitHub repository
        depth: How deep to traverse the repository
        
    Returns:
        Dict containing repository structure
    """
    # Extract owner and repo name from URL
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    def traverse_dir(path: str, current_depth: int) -> List[Dict[str, Any]]:
        if current_depth > depth:
            return []
            
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            headers=headers
        )
        
        if response.status_code != 200:
            return []
            
        contents = response.json()
        result = []
        
        for item in contents:
            if item["type"] == "dir":
                result.append({
                    "name": item["name"],
                    "path": item["path"],
                    "type": "dir",
                    "contents": traverse_dir(item["path"], current_depth + 1)
                })
            else:
                result.append({
                    "name": item["name"],
                    "path": item["path"],
                    "type": "file",
                    "size": item["size"]
                })
                
        return result
    
    return traverse_dir("", 1)

def get_file_content(repo_url: str, file_path: str) -> str:
    """
    Get content of a specific file in the repository
    
    Args:
        repo_url: URL of the GitHub repository
        file_path: Path to the file in the repository
        
    Returns:
        String containing file content
    """
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}",
        headers=headers
    )
    
    if response.status_code != 200:
        return ""
        
    content_data = response.json()
    
    if content_data.get("encoding") == "base64":
        import base64
        return base64.b64decode(content_data["content"]).decode('utf-8')
    
    return ""

# Gemini AI functions
def generate_learning_path(repo_data: Dict[str, Any], experience_level: str, focus_areas: List[str]) -> LearningPath:
    """
    Generate a learning path based on repository data using Gemini
    
    Args:
        repo_data: Repository data from GitHub API
        experience_level: User's experience level
        focus_areas: Areas to focus on
        
    Returns:
        LearningPath object with generated content
    """
    model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
    
    # Create prompt for Gemini
    prompt = f"""
    You are an expert programming tutor. Generate a learning path for a {experience_level} developer
    to understand the following GitHub repository:
    
    Repository: {repo_data['repo_info']['name']}
    Description: {repo_data['repo_info']['description']}
    Primary language: {list(repo_data['languages'].keys())[0] if repo_data['languages'] else 'Unknown'}
    
    README Content:
    {repo_data['readme'][:2000]}...
    
    Repository Structure (sample):
    {json.dumps([item for item in repo_data['contents'] if item['type'] == 'file'][:5], indent=2)}
    
    Focus areas: {', '.join(focus_areas) if focus_areas else 'All aspects'}
    
    Create a learning path with 12 chapters. For each chapter include:
    1. A clear title
    2. A concise description
    3. 3-4 specific tasks to complete
    4. 2-3 helpful tips
    5. Next steps after completing the chapter
    
    Format the response as a JSON object following this structure:
    {{
      "chapters": [
        {{
          "id": 1,
          "title": "Chapter Title",
          "description": "Chapter description",
          "tasks": ["Task 1", "Task 2", "Task 3"],
          "tips": ["Tip 1", "Tip 2"],
          "next_steps": "Next steps description"
        }},
        ...
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
        
        # Create LearningPath object
        return LearningPath(
            overall_progress=0,  # Start with 0 progress
            chapters=learning_path_data["chapters"],
            repo_name=repo_data['repo_info']['name'],
            repo_description=repo_data['repo_info']['description']
        )
    except Exception as e:
        # If parsing fails, generate a more structured response
        fallback_prompt = f"""
        There was an error generating a structured learning path. Please generate a learning path
        with exactly 12 chapters for the repository {repo_data['repo_info']['name']}.
        
        Provide ONLY a JSON object without any explanation text, following this exact structure:
        {{
          "chapters": [
            {{
              "id": 1,
              "title": "Chapter Title",
              "description": "Chapter description",
              "tasks": ["Task 1", "Task 2", "Task 3"],
              "tips": ["Tip 1", "Tip 2"],
              "next_steps": "Next steps description"
            }},
            ...11 more chapters...
          ]
        }}
        """
        
        response = model.generate_content(fallback_prompt)
        
        try:
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]
                
            learning_path_data = json.loads(json_text)
            
            return LearningPath(
                overall_progress=0,
                chapters=learning_path_data["chapters"],
                repo_name=repo_data['repo_info']['name'],
                repo_description=repo_data['repo_info']['description']
            )
        except Exception as e:
            # If still failing, create a default learning path
            chapters = []
            for i in range(1, 13):
                chapters.append(Chapter(
                    id=i,
                    title=f"Chapter {i}",
                    description=f"This is a placeholder for chapter {i}.",
                    tasks=["Review code", "Read documentation", "Try a simple change"],
                    tips=["Start with small changes", "Ask for help when stuck"],
                    next_steps="Continue to the next chapter."
                ))
                
            return LearningPath(
                overall_progress=0,
                chapters=chapters,
                repo_name=repo_data['repo_info']['name'],
                repo_description=repo_data['repo_info']['description']
            )

# Dependency to verify auth token
async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "")
    
    # In a real app, verify the token here
    # For demo purposes, we're just checking if it's not empty
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

# API endpoints
@app.post("/api/generate-learning-path")
async def create_learning_path(
    request: GitHubRepoRequest,
    token: str = Depends(verify_token)
):
    try:
        # Get repository data from GitHub
        repo_data = get_github_repo_data(request.repo_url)
        
        # Generate learning path using Gemini
        learning_path = generate_learning_path(
            repo_data, 
            request.user_experience_level,
            request.focus_areas
        )
        
        return learning_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repo-structure/{owner}/{repo}")
async def get_structure(
    owner: str, 
    repo: str,
    token: str = Depends(verify_token)
):
    repo_url = f"https://github.com/{owner}/{repo}"
    try:
        structure = get_repo_structure(repo_url)
        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-content/{owner}/{repo}/{file_path:path}")
async def get_content(
    owner: str, 
    repo: str, 
    file_path: str,
    token: str = Depends(verify_token)
):
    repo_url = f"https://github.com/{owner}/{repo}"
    try:
        content = get_file_content(repo_url, file_path)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-path")
async def get_learning_path():
    # Mock data for the demo
    return LearningPath(
        overall_progress=20,
        repo_name="sample-repo",
        repo_description="A sample repository for demonstration",
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
            ),
            # Additional chapters would be here
        ]
    )

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)