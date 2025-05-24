# GitHub API Integration for Learning Path Generator

This module integrates with the GitHub API to fetch repository data and uses Google's Gemini AI to generate personalized learning paths for developers.

## Features

- Fetch repository information from GitHub API (details, files, README, languages)
- Generate structured learning paths with chapters, tasks, tips, and next steps
- Customize learning paths based on user experience level and focus areas
- Secure API endpoints with token authentication
- Get repository file structure and file contents

## Setup

1. Create a `.env` file in the root directory with the following variables:

```
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key
```

### GitHub Token

To create a GitHub Personal Access Token:
1. Go to GitHub Settings > Developer Settings > Personal Access Tokens
2. Generate a new token with the `repo` scope
3. Copy the token to your `.env` file

### Gemini API Key

To get a Gemini API Key:
1. Go to Google AI Studio (https://ai.google.dev/)
2. Sign up or log in
3. Go to API Keys and create a new key
4. Copy the key to your `.env` file

## Usage

### Start the Server

```bash
uvicorn github_learning_path_generator:app --reload
```

### API Endpoints

#### Generate Learning Path

```
POST /api/generate-learning-path
```

Request body:
```json
{
  "repo_url": "https://github.com/owner/repo",
  "user_experience_level": "beginner", // beginner, intermediate, advanced
  "focus_areas": ["frontend", "testing"] // optional focus areas
}
```

Headers:
```
Authorization: Bearer your_access_token
```

Response:
```json
{
  "overall_progress": 0,
  "chapters": [
    {
      "id": 1,
      "title": "Chapter Title",
      "description": "Chapter description",
      "tasks": ["Task 1", "Task 2", "Task 3"],
      "tips": ["Tip 1", "Tip 2"],
      "next_steps": "Next steps description"
    },
    ...
  ],
  "repo_name": "repo",
  "repo_description": "Repository description"
}
```

#### Get Repository Structure

```
GET /api/repo-structure/{owner}/{repo}
```

Headers:
```
Authorization: Bearer your_access_token
```

Response:
```json
{
  "structure": [
    {
      "name": "src",
      "path": "src",
      "type": "dir",
      "contents": [
        {
          "name": "index.js",
          "path": "src/index.js",
          "type": "file",
          "size": 1024
        },
        ...
      ]
    },
    ...
  ]
}
```

#### Get File Content

```
GET /api/file-content/{owner}/{repo}/{file_path}
```

Headers:
```
Authorization: Bearer your_access_token
```

Response:
```json
{
  "content": "// File content here"
}
```

## Integration with Frontend

The frontend can integrate with these endpoints to:

1. Allow users to select a GitHub repository
2. Generate a personalized learning path based on the repository
3. Display the learning path with progress tracking
4. Show repository structure and file contents within the learning interface

## Error Handling

The API provides appropriate error responses with status codes and messages:

- 401: Unauthorized (missing or invalid token)
- 404: Repository or file not found
- 500: Server errors (GitHub API issues, Gemini AI errors, etc.)