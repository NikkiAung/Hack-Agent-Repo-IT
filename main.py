import os
from dotenv import load_dotenv
from backend.agents.agents import get_crew

load_dotenv()

def main():
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        print("Please set your Anthropic API key in the .env file or as an environment variable")
        return
    
    # Sample repository URL
    repo_url = "https://github.com/tiangolo/fastapi"
    
    # Get the crew
    crew = get_crew(repo_url)
    
    # Run the crew with the repository
    result = crew.kickoff(inputs={"repo_url": repo_url})
    
    print("\n" + "="*50)
    print("REPOSITORY ANALYSIS COMPLETE")
    print("="*50)
    print(result)


if __name__ == "__main__":
    main()
