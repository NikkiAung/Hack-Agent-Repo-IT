from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json
from pathlib import Path

# Create the app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create a static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Write CSS file to static directory
css_content = """
body {
    font-family: Arial, sans-serif;
    background-color: #101a23;
    color: white;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: #182533;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
h1, h2 {
    color: white;
}
form {
    margin-top: 20px;
}
label {
    display: block;
    margin-bottom: 5px;
}
input, select {
    width: 100%;
    padding: 8px;
    margin-bottom: 15px;
    background-color: #223649;
    border: 1px solid #314d68;
    color: white;
    border-radius: 4px;
}
button {
    background-color: #3d98f4;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
}
.card {
    background-color: #223649;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
}
.card h3 {
    margin-top: 0;
    color: white;
}
.card p {
    color: #90adcb;
}
.card ul {
    color: #90adcb;
}
.progress-container {
    height: 8px;
    background-color: #314d68;
    border-radius: 4px;
    margin: 10px 0;
    overflow: hidden;
}
.progress-bar {
    height: 100%;
    background-color: #3d98f4;
    border-radius: 4px;
    width: 25%;
    transition: width 1s ease-in-out;
}
.results {
    margin-top: 30px;
}
.progress-text {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
}
.progress-text span:first-child {
    color: #90adcb;
}
.progress-text span:last-child {
    color: #3d98f4;
    font-weight: bold;
}
"""

with open(static_dir / "style.css", "w") as f:
    f.write(css_content)

# Create a simple HTML form
simple_form = """
<!DOCTYPE html>
<html>
<head>
    <title>GitHub Onboarding Generator</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>GitHub Onboarding Generator</h1>
        <p>Generate a personalized onboarding path for any GitHub repository.</p>
        
        <form method="post">
            <div>
                <label for="repo_url">GitHub Repository URL:</label>
                <input type="text" id="repo_url" name="repo_url" 
                       placeholder="https://github.com/username/repository" 
                       value="{{ repo_url }}" required>
            </div>
            <div>
                <label for="experience">Experience Level:</label>
                <select id="experience" name="experience">
                    <option value="beginner" {% if experience == 'beginner' %}selected{% endif %}>Beginner</option>
                    <option value="intermediate" {% if experience == 'intermediate' %}selected{% endif %}>Intermediate</option>
                    <option value="advanced" {% if experience == 'advanced' %}selected{% endif %}>Advanced</option>
                </select>
            </div>
            <button type="submit">Generate Onboarding Path</button>
        </form>
        
        {% if generated %}
        <div class="results">
            <h2>Generated Onboarding Path</h2>
            
            <div class="card">
                <h3>Overall Progress</h3>
                <div class="progress-container">
                    <div class="progress-bar" style="width: 25%;"></div>
                </div>
                <div class="progress-text">
                    <span>Getting Started</span>
                    <span>25%</span>
                </div>
            </div>
            
            {% for chapter in chapters %}
            <div class="card">
                <h3>{{ chapter.id }}. {{ chapter.title }}</h3>
                <p>{{ chapter.description }}</p>
                
                <h4>Tasks:</h4>
                <ul>
                    {% for task in chapter.tasks %}
                    <li>{{ task }}</li>
                    {% endfor %}
                </ul>
                
                <h4>Tips:</h4>
                <ul>
                    {% for tip in chapter.tips %}
                    <li>{{ tip }}</li>
                    {% endfor %}
                </ul>
                
                <h4>Next Steps:</h4>
                <p>{{ chapter.next_steps }}</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                if (document.querySelector('.progress-bar')) {
                    // Animate the progress bar after page load
                    const progressBar = document.querySelector('.progress-bar');
                    progressBar.style.width = '0%';
                    
                    setTimeout(function() {
                        progressBar.style.width = '25%';
                    }, 300);
                }
            });
        </script>
    </div>
</body>
</html>
"""

# Write the template file
with open(templates_dir / "simple_form.html", "w") as f:
    f.write(simple_form)

# Set up templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define some example chapters
def get_example_chapters(repo_url):
    repo_parts = repo_url.strip('/').split('/')
    repo_name = repo_parts[-1] if len(repo_parts) >= 2 else "example-repo"
    
    return [
        {
            "id": 1,
            "title": "Repository Overview & Setup",
            "description": f"Get familiar with the {repo_name} repository and set up your local environment.",
            "tasks": [
                "Clone the repository locally",
                "Read the README.md file",
                "Identify the main components and features"
            ],
            "tips": [
                "Pay special attention to any setup instructions in the README",
                "Look for .env.example files to configure your environment"
            ],
            "next_steps": "Once your environment is set up, explore the codebase structure."
        },
        {
            "id": 2,
            "title": "Git Workflow & Branching",
            "description": "Learn how the team uses Git for collaboration and development.",
            "tasks": [
                "Understand the branching model (Git Flow, GitHub Flow, etc.)",
                "Learn branch naming conventions",
                "Practice creating a feature branch and making a commit"
            ],
            "tips": [
                "Look for CONTRIBUTING.md or similar documentation",
                "Check the commit history to see patterns in commit messages"
            ],
            "next_steps": "After understanding the Git workflow, explore the code style and architecture."
        },
        {
            "id": 3,
            "title": "Code Style & Linters",
            "description": "Understand the coding standards and tools used to maintain code quality.",
            "tasks": [
                "Identify linters and formatting tools (ESLint, Prettier, etc.)",
                "Set up your IDE with recommended extensions",
                "Run linters and fix any issues"
            ],
            "tips": [
                "Look for .eslintrc, .prettierrc, or similar configuration files",
                "Check package.json for linting scripts"
            ],
            "next_steps": "With your environment set up and code style understood, dive into the architecture."
        },
        {
            "id": 4,
            "title": "Testing & Quality Assurance",
            "description": "Learn how the project ensures code quality through testing.",
            "tasks": [
                "Identify the testing frameworks used",
                "Run the test suite",
                "Write a simple test for a feature"
            ],
            "tips": [
                "Look for test directories like 'tests', '__tests__', etc.",
                "Check package.json or other config files for test scripts"
            ],
            "next_steps": "After understanding testing, learn about the deployment process."
        }
    ]

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse(
        "simple_form.html", 
        {"request": request, "repo_url": "", "experience": "beginner", "generated": False}
    )

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, repo_url: str = Form(...), experience: str = Form(...)):
    # Generate example chapters based on the repo URL
    chapters = get_example_chapters(repo_url)
    
    return templates.TemplateResponse(
        "simple_form.html", 
        {
            "request": request,
            "repo_url": repo_url,
            "experience": experience,
            "generated": True,
            "chapters": chapters
        }
    )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)