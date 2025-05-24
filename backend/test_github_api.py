#!/usr/bin/env python3
"""
Simple command-line tool to test the GitHub API functionality.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_repo_info(repo_url):
    """Extract owner and repo name from a GitHub URL"""
    parts = repo_url.strip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def fetch_repo_info(repo_url):
    """Fetch basic repository information"""
    owner, repo = get_repo_info(repo_url)
    
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    else:
        print("Warning: No GitHub token found in .env file.")
    
    # Make API request
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}", 
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json().get('message', 'Unknown error'))
        return None

def fetch_repo_languages(repo_url):
    """Fetch languages used in the repository"""
    owner, repo = get_repo_info(repo_url)
    
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/languages", 
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def main():
    print("GitHub Repository Analyzer")
    print("==========================")
    
    repo_url = input("Enter GitHub repository URL: ")
    if not repo_url:
        repo_url = "https://github.com/facebook/react"  # Default for testing
    
    print(f"\nFetching information for {repo_url}...")
    
    # Get basic repo info
    repo_info = fetch_repo_info(repo_url)
    if not repo_info:
        print("Failed to fetch repository information.")
        return
    
    # Get languages
    languages = fetch_repo_languages(repo_url)
    
    # Display results
    print("\nRepository Information:")
    print(f"Name: {repo_info['name']}")
    print(f"Description: {repo_info['description']}")
    print(f"Default Branch: {repo_info['default_branch']}")
    print(f"Stars: {repo_info['stargazers_count']}")
    print(f"Forks: {repo_info['forks_count']}")
    
    print("\nLanguages:")
    for lang, bytes_count in languages.items():
        percentage = bytes_count / sum(languages.values()) * 100
        print(f"- {lang}: {percentage:.1f}%")
    
    print("\nThis information would be used to generate a personalized onboarding path.")

if __name__ == "__main__":
    main()