from tabnanny import verbose


def main():
    """Demo the updated CrewAI agents with Anthropic Claude."""
    import os
    from backend.agents.agents import get_crew
    
    # Check if required environment variables are set
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        print("See .env.example for reference.")
        return
    
    # print("🚀 Starting Hack Agent Repo IT with Anthropic Claude...")
    print("✅ All required environment variables are set.")
    
    # Initialize the crew
    crew = get_crew()
    
    # Example: Analyze a repository
    repo_url = "https://github.com/tiangolo/fastapi"
    print(f"\n📊 Analyzing repository: {repo_url}")
    
    try:
        result = crew.kickoff(inputs={"repo_url": repo_url}, verbose= True)
        print("\n=== ANALYSIS RESULT ===")
        print(result)
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("This is expected if external services (Qdrant, etc.) are not running.")


if __name__ == "__main__":
    main()
