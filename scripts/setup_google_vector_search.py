#!/usr/bin/env python3
"""
Google Cloud Vector Search Setup Script

This script sets up Google Cloud Vector Search without requiring an existing Weaviate instance.
Use this when you want to start fresh with Google Vector Search.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from services.google_vector_search_service import GoogleVectorSearchService
except ImportError:
    print("Error: Could not import GoogleVectorSearchService")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Load environment variables
load_dotenv()

class GoogleVectorSearchSetup:
    """Setup Google Cloud Vector Search from scratch"""
    
    def __init__(self):
        self.google_service = None
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log setup progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.setup_log.append(log_entry)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log("Checking prerequisites...")
        
        required_env_vars = [
            "GOOGLE_CLOUD_PROJECT",
            "GEMINI_API_KEY"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"Missing required environment variables: {', '.join(missing_vars)}", "ERROR")
            self.log("Please set the following in your .env file:", "INFO")
            for var in missing_vars:
                if var == "GOOGLE_CLOUD_PROJECT":
                    self.log(f"  {var}=your-google-cloud-project-id", "INFO")
                elif var == "GEMINI_API_KEY":
                    self.log(f"  {var}=your-gemini-api-key", "INFO")
            return False
        
        # Check Google Cloud SDK installation
        try:
            from google.cloud import aiplatform
            from google import genai
            from google.cloud import storage
            self.log("✓ Google Cloud SDK available")
        except ImportError as e:
            self.log(f"✗ Google Cloud SDK not available: {e}", "ERROR")
            self.log("Install with: pip install google-cloud-aiplatform google-genai google-cloud-storage", "INFO")
            return False
        
        # Check Google Cloud authentication
        try:
            from google.auth import default
            credentials, project = default()
            if project:
                self.log(f"✓ Google Cloud authentication configured for project: {project}")
            else:
                self.log("⚠ Google Cloud authentication may not be properly configured", "WARNING")
                self.log("Run: gcloud auth application-default login", "INFO")
        except Exception as e:
            self.log(f"⚠ Google Cloud authentication check failed: {e}", "WARNING")
            self.log("Run: gcloud auth application-default login", "INFO")
        
        self.log("✓ All prerequisites met")
        return True
    
    def setup_google_service(self) -> bool:
        """Setup Google Cloud Vector Search service"""
        try:
            self.google_service = GoogleVectorSearchService()
            status = self.google_service.get_status()
            
            if status["genai_client_available"]:
                self.log("✓ Google Vector Search service initialized")
                self.log(f"  Project: {status['project_id']}")
                self.log(f"  Location: {status['location']}")
                self.log(f"  Embedding Model: {status['embedding_model']}")
                return True
            else:
                self.log("✗ Failed to initialize Google Vector Search service", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ Failed to setup Google service: {e}", "ERROR")
            return False
    
    def get_sample_data(self) -> List[Dict[str, Any]]:
        """Get sample data for testing"""
        return [
            {
                "id": "sample_1",
                "repository_id": "fastapi",
                "repository_url": "https://github.com/tiangolo/fastapi",
                "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It provides automatic API documentation, data validation, and serialization.",
                "type": "summary",
                "module_name": "overview",
                "module_path": "README.md",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "sample_2",
                "repository_id": "fastapi",
                "repository_url": "https://github.com/tiangolo/fastapi",
                "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n\n@app.get('/items/{item_id}')\ndef read_item(item_id: int, q: str = None):\n    return {'item_id': item_id, 'q': q}",
                "type": "code",
                "module_name": "main",
                "module_path": "main.py",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "sample_3",
                "repository_id": "django",
                # "repository_url": "https://github.com/django/django",
                "repository_url":"https://github.com/microsoft/magentic-ui",
                "content": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of web development.",
                "type": "summary",
                "module_name": "overview",
                "module_path": "README.rst",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def setup_google_infrastructure(self) -> bool:
        """Setup Google Cloud Vector Search infrastructure"""
        if not self.google_service:
            return False
        
        try:
            self.log("Setting up Google Cloud Vector Search infrastructure...")
            self.log("This process may take 45-60 minutes due to infrastructure provisioning.")
            
            # Create Vector Search index
            self.log("Creating Vector Search index (this may take 20-30 minutes)...")
            index_created = await self.google_service.create_vector_search_index()
            
            if not index_created:
                self.log("Failed to create Vector Search index", "ERROR")
                return False
            
            # Create and deploy index endpoint
            self.log("Creating and deploying index endpoint (this may take 10-30 minutes)...")
            endpoint_created = await self.google_service.create_index_endpoint()
            
            if not endpoint_created:
                self.log("Failed to create index endpoint", "ERROR")
                return False
            
            self.log("✓ Google Cloud Vector Search infrastructure ready")
            return True
            
        except Exception as e:
            self.log(f"Error setting up Google infrastructure: {e}", "ERROR")
            return False
    
    async def add_sample_data(self) -> bool:
        """Add sample data to test the system"""
        if not self.google_service:
            return False
        
        try:
            documents = self.get_sample_data()
            self.log(f"Adding {len(documents)} sample documents...")
            
            success = await self.google_service.add_documents(documents)
            
            if success:
                self.log(f"✓ Successfully added {len(documents)} sample documents")
                return True
            else:
                self.log("Failed to add sample documents", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error adding sample data: {e}", "ERROR")
            return False
    
    async def test_system(self) -> bool:
        """Test the Google Vector Search system"""
        if not self.google_service:
            return False
        
        try:
            self.log("Testing Google Vector Search system...")
            
            # Test queries
            test_queries = [
                "What is FastAPI?",
                "How to create a simple API?",
                "What is this?"
            ]
            
            for query in test_queries:
                self.log(f"Testing query: {query}")
                result = await self.google_service.query(query)
                
                if result and "answer" in result:
                    self.log(f"✓ Query successful: {result['answer'][:100]}...")
                else:
                    self.log(f"⚠ Query returned no results", "WARNING")
            
            self.log("✓ System testing completed")
            return True
                
        except Exception as e:
            self.log(f"Error testing system: {e}", "ERROR")
            return False
    
    def save_setup_log(self):
        """Save setup log to file"""
        log_file = f"google_vector_search_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(log_file, 'w') as f:
                f.write("\n".join(self.setup_log))
            self.log(f"Setup log saved to {log_file}")
        except Exception as e:
            self.log(f"Failed to save setup log: {e}", "ERROR")
    
    async def run_setup(self):
        """Run the complete setup process"""
        self.log("🚀 Starting Google Cloud Vector Search setup...")
        self.log("This process may take 45-60 minutes due to infrastructure setup.")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites not met. Aborting setup.", "ERROR")
            return False
        
        # Setup Google service
        if not self.setup_google_service():
            self.log("Failed to setup Google service. Aborting setup.", "ERROR")
            return False
        
        # Setup infrastructure
        if not await self.setup_google_infrastructure():
            self.log("Failed to setup Google infrastructure. Aborting setup.", "ERROR")
            return False
        
        # Add sample data
        if not await self.add_sample_data():
            self.log("Failed to add sample data. Continuing anyway...", "WARNING")
        
        # Test system
        if not await self.test_system():
            self.log("System testing failed. Setup may be incomplete.", "WARNING")
        
        self.log("✅ Google Cloud Vector Search setup completed successfully!")
        self.log("")
        self.log("Next steps:")
        self.log("1. Update your application to use HybridRAGService with Google Vector Search preference")
        self.log("2. Add your repository data using the GoogleVectorSearchService.add_documents() method")
        self.log("3. Test queries using the query() method")
        
        return True

def print_setup_instructions():
    """Print setup instructions"""
    print("""
🔧 Google Cloud Vector Search Setup Instructions

1. Prerequisites:
   - Google Cloud Project with billing enabled
   - Vertex AI API enabled
   - Gemini API key
   - Google Cloud SDK installed and authenticated

2. Required APIs to enable:
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage.googleapis.com

3. Authentication:
   gcloud auth application-default login

4. Environment Variables (.env file):
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1  # optional, defaults to us-central1
   GEMINI_API_KEY=your-gemini-api-key

5. Install Dependencies:
   pip install google-cloud-aiplatform google-genai google-cloud-storage

6. Cost Considerations:
   - Vector Search index: ~$50-100/month
   - Endpoint deployment: ~$200-400/month
   - Embedding generation: ~$0.0001 per 1K tokens
   - Storage: ~$0.02 per GB/month

7. Time Requirements:
   - Initial setup: 45-60 minutes
   - Index creation: 20-30 minutes
   - Endpoint deployment: 10-30 minutes

For more details, see: docs/GOOGLE_VECTOR_SEARCH_MIGRATION.md
""")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Google Cloud Vector Search")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if args.setup:
        print_setup_instructions()
        return
    
    print("🚀 Google Cloud Vector Search Setup")
    print("This will set up Google Cloud Vector Search with Gemini embeddings.")
    print("This process may take 45-60 minutes due to infrastructure setup.")
    print("")
    print("For setup instructions, run: python scripts/setup_google_vector_search.py --setup")
    print("")
    
    if not args.yes:
        response = input("Do you want to continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    setup = GoogleVectorSearchSetup()
    
    try:
        success = await setup.run_setup()
        
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Check the logs for details.")
            
    except KeyboardInterrupt:
        print("\n⚠ Setup interrupted by user.")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
    finally:
        setup.save_setup_log()

if __name__ == "__main__":
    asyncio.run(main())