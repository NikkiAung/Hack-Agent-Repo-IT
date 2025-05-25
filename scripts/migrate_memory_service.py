#!/usr/bin/env python3
"""
Memory Service Migration Script

This script helps migrate from the old Neo4j/Weaviate-based MemoryService
to the new Google Vector Search-based implementation.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.memory_service import MemoryService
from services.google_vector_search_service import GoogleVectorSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryServiceMigrator:
    """Handles migration from old memory service to new Google Vector Search implementation"""
    
    def __init__(self):
        self.new_memory_service = MemoryService()
        self.migration_log = []
        
    async def check_old_system_status(self) -> Dict[str, Any]:
        """Check if old Neo4j/Weaviate systems are accessible"""
        status = {
            "neo4j": {"available": False, "error": None},
            "weaviate": {"available": False, "error": None}
        }
        
        # Check Neo4j
        try:
            from neo4j import GraphDatabase
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            driver.close()
            status["neo4j"]["available"] = True
            logger.info("Neo4j connection successful")
        except Exception as e:
            status["neo4j"]["error"] = str(e)
            logger.warning(f"Neo4j not available: {e}")
        
        # Check Weaviate
        try:
            import weaviate
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
            
            auth_config = None
            if weaviate_api_key:
                auth_config = weaviate.AuthApiKey(api_key=weaviate_api_key)
            
            client = weaviate.Client(url=weaviate_url, auth_client_secret=auth_config)
            client.schema.get()
            status["weaviate"]["available"] = True
            logger.info("Weaviate connection successful")
        except Exception as e:
            status["weaviate"]["error"] = str(e)
            logger.warning(f"Weaviate not available: {e}")
        
        return status
    
    async def export_neo4j_data(self) -> Optional[List[Dict[str, Any]]]:
        """Export repository data from Neo4j"""
        try:
            from neo4j import GraphDatabase
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7474")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            repositories = []
            
            with driver.session() as session:
                # Get all repositories
                repo_result = session.run(
                    """
                    MATCH (r:Repository)
                    RETURN r.id as id, r.url as url, r.name as name,
                           r.description as description, r.last_analyzed as last_analyzed,
                           r.analysis_type as analysis_type
                    """
                )
                
                for repo_record in repo_result:
                    repo_id = repo_record["id"]
                    
                    # Get modules for this repository
                    module_result = session.run(
                        """
                        MATCH (r:Repository {id: $repo_id})-[:CONTAINS]->(m:Module)
                        RETURN m.name as name, m.path as path, m.type as type,
                               m.complexity as complexity, m.lines_of_code as lines_of_code
                        """,
                        repo_id=repo_id
                    )
                    
                    modules = []
                    for module_record in module_result:
                        modules.append({
                            "name": module_record["name"],
                            "path": module_record["path"],
                            "type": module_record["type"],
                            "complexity": module_record["complexity"],
                            "lines_of_code": module_record["lines_of_code"]
                        })
                    
                    # Get dependencies for this repository
                    dep_result = session.run(
                        """
                        MATCH (r:Repository {id: $repo_id})-[:DEPENDS_ON]->(d:Dependency)
                        RETURN d.name as name, d.version as version, d.type as type
                        """,
                        repo_id=repo_id
                    )
                    
                    dependencies = []
                    for dep_record in dep_result:
                        dependencies.append({
                            "name": dep_record["name"],
                            "version": dep_record["version"],
                            "type": dep_record["type"]
                        })
                    
                    repositories.append({
                        "repository_id": repo_id,
                        "repository_url": repo_record["url"],
                        "repository_name": repo_record["name"],
                        "description": repo_record["description"],
                        "last_analyzed": repo_record["last_analyzed"],
                        "analysis_type": repo_record["analysis_type"],
                        "modules": modules,
                        "dependencies": dependencies
                    })
            
            driver.close()
            logger.info(f"Exported {len(repositories)} repositories from Neo4j")
            return repositories
            
        except Exception as e:
            logger.error(f"Error exporting Neo4j data: {e}")
            return None
    
    async def export_weaviate_data(self) -> Optional[List[Dict[str, Any]]]:
        """Export content data from Weaviate"""
        try:
            import weaviate
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
            
            auth_config = None
            if weaviate_api_key:
                auth_config = weaviate.AuthApiKey(api_key=weaviate_api_key)
            
            client = weaviate.Client(url=weaviate_url, auth_client_secret=auth_config)
            
            # Get all RepositoryContent objects
            result = client.query.get("RepositoryContent", [
                "repository_id", "repository_url", "content", "type",
                "module_name", "module_path", "timestamp"
            ]).do()
            
            content_data = []
            if "data" in result and "Get" in result["data"] and "RepositoryContent" in result["data"]["Get"]:
                content_data = result["data"]["Get"]["RepositoryContent"]
            
            logger.info(f"Exported {len(content_data)} content items from Weaviate")
            return content_data
            
        except Exception as e:
            logger.error(f"Error exporting Weaviate data: {e}")
            return None
    
    async def migrate_repository_data(
        self,
        neo4j_data: List[Dict[str, Any]],
        weaviate_data: List[Dict[str, Any]]
    ) -> bool:
        """Migrate repository data to new Google Vector Search system"""
        try:
            # Group Weaviate content by repository_id
            content_by_repo = {}
            for content in weaviate_data:
                repo_id = content.get("repository_id")
                if repo_id:
                    if repo_id not in content_by_repo:
                        content_by_repo[repo_id] = []
                    content_by_repo[repo_id].append(content)
            
            # Migrate each repository
            for repo_data in neo4j_data:
                repo_id = repo_data["repository_id"]
                repo_url = repo_data["repository_url"]
                
                # Prepare analysis results format
                analysis_results = {
                    "repository_name": repo_data.get("repository_name", ""),
                    "description": repo_data.get("description", ""),
                    "modules": repo_data.get("modules", []),
                    "dependencies": repo_data.get("dependencies", [])
                }
                
                # Add content from Weaviate
                repo_content = content_by_repo.get(repo_id, [])
                for content in repo_content:
                    if content.get("type") == "summary":
                        analysis_results["summary"] = content.get("content", "")
                    elif content.get("type") == "module_doc":
                        # Find corresponding module and add documentation
                        module_name = content.get("module_name", "")
                        for module in analysis_results["modules"]:
                            if module.get("name") == module_name:
                                module["documentation"] = content.get("content", "")
                                break
                
                # Store in new system
                try:
                    new_repo_id = await self.new_memory_service.store_analysis_results(
                        repo_url=repo_url,
                        results=analysis_results,
                        analysis_type=repo_data.get("analysis_type", "migrated")
                    )
                    
                    self.migration_log.append({
                        "status": "success",
                        "repo_url": repo_url,
                        "old_repo_id": repo_id,
                        "new_repo_id": new_repo_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.info(f"Successfully migrated repository: {repo_url}")
                    
                except Exception as e:
                    self.migration_log.append({
                        "status": "error",
                        "repo_url": repo_url,
                        "old_repo_id": repo_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.error(f"Failed to migrate repository {repo_url}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return False
    
    async def save_migration_log(self, filename: str = None) -> str:
        """Save migration log to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_service_migration_{timestamp}.json"
        
        log_data = {
            "migration_timestamp": datetime.now().isoformat(),
            "total_repositories": len(self.migration_log),
            "successful_migrations": len([log for log in self.migration_log if log["status"] == "success"]),
            "failed_migrations": len([log for log in self.migration_log if log["status"] == "error"]),
            "migration_details": self.migration_log
        }
        
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Migration log saved to: {filename}")
        return filename
    
    async def run_migration(self, export_backup: bool = True) -> bool:
        """Run the complete migration process"""
        logger.info("Starting Memory Service migration...")
        
        # Check old system status
        status = await self.check_old_system_status()
        
        if not status["neo4j"]["available"] and not status["weaviate"]["available"]:
            logger.warning("Neither Neo4j nor Weaviate are available. Nothing to migrate.")
            return True
        
        # Export data from old systems
        neo4j_data = []
        weaviate_data = []
        
        if status["neo4j"]["available"]:
            neo4j_data = await self.export_neo4j_data() or []
        
        if status["weaviate"]["available"]:
            weaviate_data = await self.export_weaviate_data() or []
        
        if not neo4j_data and not weaviate_data:
            logger.info("No data found to migrate.")
            return True
        
        # Save backup if requested
        if export_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_data = {
                "export_timestamp": datetime.now().isoformat(),
                "neo4j_data": neo4j_data,
                "weaviate_data": weaviate_data
            }
            
            backup_filename = f"memory_service_backup_{timestamp}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Backup saved to: {backup_filename}")
        
        # Migrate data to new system
        success = await self.migrate_repository_data(neo4j_data, weaviate_data)
        
        # Save migration log
        log_filename = await self.save_migration_log()
        
        if success:
            logger.info("Migration completed successfully!")
            logger.info(f"Migration log: {log_filename}")
        else:
            logger.error("Migration completed with errors. Check the migration log for details.")
        
        return success

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Memory Service to Google Vector Search")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup of old data"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check old system status, don't migrate"
    )
    
    args = parser.parse_args()
    
    migrator = MemoryServiceMigrator()
    
    if args.check_only:
        status = await migrator.check_old_system_status()
        print("\nOld System Status:")
        print(f"Neo4j: {'✓' if status['neo4j']['available'] else '✗'} {status['neo4j'].get('error', '')}")
        print(f"Weaviate: {'✓' if status['weaviate']['available'] else '✗'} {status['weaviate'].get('error', '')}")
        return
    
    # Run migration
    success = await migrator.run_migration(export_backup=not args.no_backup)
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the new Google Vector Search system")
        print("2. Update your applications to use the new MemoryService")
        print("3. Consider removing Neo4j and Weaviate dependencies if no longer needed")
    else:
        print("\n❌ Migration completed with errors. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())