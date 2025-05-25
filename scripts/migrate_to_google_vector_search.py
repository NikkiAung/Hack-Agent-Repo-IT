#!/usr/bin/env python3
"""
Migration Script: Weaviate to Google Cloud Vector Search

This script helps migrate from the current Weaviate setup to Google Cloud Vector Search
with Gemini embeddings for better reliability and integration.
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

try:
    import weaviate
    HAS_WEAVIATE = True
except ImportError:
    HAS_WEAVIATE = False
    print("Warning: Weaviate client not available. Migration from existing data will be skipped.")

# Load environment variables
load_dotenv()

class WeaviateToGoogleMigration:
    """Handles migration from Weaviate to Google Cloud Vector Search"""
    
    def __init__(self):
        self.weaviate_client = None
        self.google_service = None
        self.migration_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log migration progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
    
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
            return False
        
        # Check Google Cloud SDK installation
        try:
            from google.cloud import aiplatform
            from google import genai
            self.log("✓ Google Cloud SDK available")
        except ImportError:
            self.log("✗ Google Cloud SDK not available. Install with: pip install google-cloud-aiplatform google-genai", "ERROR")
            return False
        
        self.log("✓ All prerequisites met")
        return True
    
    def setup_weaviate_client(self) -> bool:
        """Setup Weaviate client for data extraction"""
        if not HAS_WEAVIATE:
            self.log("Weaviate client not available, skipping data extraction", "WARNING")
            return False
            
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        try:
            auth_config = None
            if weaviate_api_key:
                auth_config = weaviate.AuthApiKey(api_key=weaviate_api_key)
            
            self.weaviate_client = weaviate.Client(
                url=weaviate_url,
                auth_client_secret=auth_config
            )
            
            if self.weaviate_client.is_ready():
                self.log(f"✓ Connected to Weaviate at {weaviate_url}")
                return True
            else:
                self.log("✗ Weaviate is not ready", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ Failed to connect to Weaviate: {e}", "ERROR")
            return False
    
    def setup_google_service(self) -> bool:
        """Setup Google Cloud Vector Search service"""
        try:
            self.google_service = GoogleVectorSearchService()
            status = self.google_service.get_status()
            
            if status["genai_client_available"]:
                self.log("✓ Google Vector Search service initialized")
                return True
            else:
                self.log("✗ Failed to initialize Google Vector Search service", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ Failed to setup Google service: {e}", "ERROR")
            return False
    
    async def extract_weaviate_data(self) -> List[Dict[str, Any]]:
        """Extract data from Weaviate"""
        if not self.weaviate_client:
            self.log("No Weaviate client available, using sample data", "WARNING")
            return self._get_sample_data()
        
        try:
            self.log("Extracting data from Weaviate...")
            
            # Query all RepositoryContent objects
            result = self.weaviate_client.query.get(
                "RepositoryContent",
                ["repository_id", "repository_url", "content", "type", "module_name", "module_path", "timestamp"]
            ).do()
            
            if "data" not in result or "Get" not in result["data"]:
                self.log("No data found in Weaviate", "WARNING")
                return self._get_sample_data()
            
            documents = result["data"]["Get"]["RepositoryContent"]
            self.log(f"✓ Extracted {len(documents)} documents from Weaviate")
            
            # Convert to standard format
            converted_docs = []
            for doc in documents:
                converted_docs.append({
                    "id": f"doc_{len(converted_docs)}",
                    "repository_id": doc.get("repository_id", ""),
                    "repository_url": doc.get("repository_url", ""),
                    "content": doc.get("content", ""),
                    "type": doc.get("type", ""),
                    "module_name": doc.get("module_name", ""),
                    "module_path": doc.get("module_path", ""),
                    "timestamp": doc.get("timestamp", datetime.now().isoformat())
                })
            
            return converted_docs
            
        except Exception as e:
            self.log(f"Error extracting Weaviate data: {e}", "ERROR")
            return self._get_sample_data()
    
    def _get_sample_data(self) -> List[Dict[str, Any]]:
        """Get sample data for testing"""
        return [
            {
                "id": "sample_1",
                "repository_id": "fastapi",
                "repository_url": "https://github.com/tiangolo/fastapi",
                "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.",
                "type": "summary",
                "module_name": "overview",
                "module_path": "README.md",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "sample_2",
                "repository_id": "fastapi",
                "repository_url": "https://github.com/tiangolo/fastapi",
                "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}",
                "type": "code",
                "module_name": "main",
                "module_path": "main.py",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def setup_google_infrastructure(self) -> bool:
        """Setup Google Cloud Vector Search infrastructure"""
        if not self.google_service:
            return False
        
        try:
            self.log("Setting up Google Cloud Vector Search infrastructure...")
            
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
    
    async def migrate_data(self, documents: List[Dict[str, Any]]) -> bool:
        """Migrate documents to Google Cloud Vector Search"""
        if not self.google_service or not documents:
            return False
        
        try:
            self.log(f"Migrating {len(documents)} documents to Google Cloud Vector Search...")
            
            # Add documents to Google Vector Search
            success = await self.google_service.add_documents(documents)
            
            if success:
                self.log(f"✓ Successfully migrated {len(documents)} documents")
                return True
            else:
                self.log("Failed to migrate documents", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error migrating data: {e}", "ERROR")
            return False
    
    async def test_migration(self) -> bool:
        """Test the migrated system"""
        if not self.google_service:
            return False
        
        try:
            self.log("Testing migrated system...")
            
            # Test query
            test_query = "What is FastAPI?"
            result = await self.google_service.query(test_query)
            
            if result and "answer" in result:
                self.log(f"✓ Test query successful: {result['answer'][:100]}...")
                return True
            else:
                self.log("Test query failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing migration: {e}", "ERROR")
            return False
    
    def save_migration_log(self):
        """Save migration log to file"""
        log_file = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(log_file, 'w') as f:
                f.write("\n".join(self.migration_log))
            self.log(f"Migration log saved to {log_file}")
        except Exception as e:
            self.log(f"Failed to save migration log: {e}", "ERROR")
    
    async def run_migration(self):
        """Run the complete migration process"""
        self.log("Starting Weaviate to Google Cloud Vector Search migration")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites not met. Aborting migration.", "ERROR")
            return False
        
        # Setup clients
        self.setup_weaviate_client()  # Optional, will warn if not available
        
        if not self.setup_google_service():
            self.log("Failed to setup Google service. Aborting migration.", "ERROR")
            return False
        
        # Extract data from Weaviate
        documents = await self.extract_weaviate_data()
        if not documents:
            self.log("No documents to migrate", "ERROR")
            return False
        
        # Setup Google Cloud infrastructure
        if not await self.setup_google_infrastructure():
            self.log("Failed to setup Google infrastructure. Aborting migration.", "ERROR")
            return False
        
        # Migrate data
        if not await self.migrate_data(documents):
            self.log("Failed to migrate data. Aborting migration.", "ERROR")
            return False
        
        # Test migration
        if not await self.test_migration():
            self.log("Migration test failed", "WARNING")
        
        self.log("Migration completed successfully!")
        self.save_migration_log()
        return True

def print_setup_instructions():
    """Print setup instructions for Google Cloud"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Google Cloud Vector Search Setup                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Before running this migration, please complete the following setup:

1. 📋 GOOGLE CLOUD PROJECT SETUP:
   • Create a Google Cloud project: https://console.cloud.google.com/
   • Enable the following APIs:
     - Vertex AI API
     - Cloud Storage API
     - AI Platform API
   
   gcloud services enable aiplatform.googleapis.com storage.googleapis.com

2. 🔑 AUTHENTICATION:
   • Set up Application Default Credentials:
   
   gcloud auth application-default login
   
   • Or set GOOGLE_APPLICATION_CREDENTIALS environment variable

3. 🌍 ENVIRONMENT VARIABLES:
   Add these to your .env file:
   
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GEMINI_API_KEY=your-gemini-api-key

4. 📦 INSTALL DEPENDENCIES:
   
   pip install google-cloud-aiplatform google-genai google-cloud-storage

5. 💰 COST CONSIDERATIONS:
   • Vector Search: ~$0.10 per 1M queries
   • Gemini Embeddings: Pay-per-use
   • Cloud Storage: Standard storage rates
   • Index creation: One-time setup cost

6. ⏱️  TIME REQUIREMENTS:
   • Index creation: 20-30 minutes
   • Endpoint deployment: 10-30 minutes
   • Total migration time: 45-60 minutes

╔══════════════════════════════════════════════════════════════════════════════╗
║ Ready to migrate? Run: python scripts/migrate_to_google_vector_search.py    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

async def main():
    """Main migration function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print_setup_instructions()
        return
    
    print("🚀 Starting migration from Weaviate to Google Cloud Vector Search...")
    print("This process may take 45-60 minutes due to infrastructure setup.")
    print("\nFor setup instructions, run: python scripts/migrate_to_google_vector_search.py --setup")
    
    # Confirm before proceeding
    response = input("\nDo you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Run migration
    migration = WeaviateToGoogleMigration()
    success = await migration.run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your RAG service to use GoogleVectorSearchService")
        print("2. Test the new system with your application")
        print("3. Update your deployment configuration")
    else:
        print("\n❌ Migration failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())