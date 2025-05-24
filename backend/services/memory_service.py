import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

try:
    import weaviate
except ImportError:
    weaviate = None

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing repository analysis memory and relationships"""
    
    def __init__(self):
        self.neo4j_driver = None
        self.weaviate_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database connections"""
        # Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        if GraphDatabase:
            try:
                self.neo4j_driver = GraphDatabase.driver(
                    neo4j_uri,
                    auth=(neo4j_user, neo4j_password)
                )
                logger.info("Connected to Neo4j")
            except Exception as e:
                logger.warning(f"Failed to connect to Neo4j: {e}")
        
        # Weaviate connection
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        if weaviate:
            try:
                auth_config = None
                if weaviate_api_key:
                    auth_config = weaviate.AuthApiKey(api_key=weaviate_api_key)
                
                self.weaviate_client = weaviate.Client(
                    url=weaviate_url,
                    auth_client_secret=auth_config
                )
                logger.info("Connected to Weaviate")
            except Exception as e:
                logger.warning(f"Failed to connect to Weaviate: {e}")
    
    async def store_analysis_results(
        self,
        repo_url: str,
        results: Dict[str, Any],
        analysis_type: str = "full"
    ) -> str:
        """Store analysis results in memory systems"""
        try:
            repo_id = self._generate_repo_id(repo_url)
            
            # Store in Neo4j (relationships and metadata)
            if self.neo4j_driver:
                await self._store_in_neo4j(repo_id, repo_url, results, analysis_type)
            
            # Store in Weaviate (vector embeddings)
            if self.weaviate_client:
                await self._store_in_weaviate(repo_id, repo_url, results)
            
            logger.info(f"Stored analysis results for {repo_url}")
            return repo_id
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            raise
    
    async def _store_in_neo4j(
        self,
        repo_id: str,
        repo_url: str,
        results: Dict[str, Any],
        analysis_type: str
    ):
        """Store repository data and relationships in Neo4j"""
        if not self.neo4j_driver:
            return
        
        with self.neo4j_driver.session() as session:
            # Create repository node
            session.run(
                """
                MERGE (r:Repository {id: $repo_id})
                SET r.url = $repo_url,
                    r.last_analyzed = datetime(),
                    r.analysis_type = $analysis_type,
                    r.name = $name,
                    r.description = $description
                """,
                repo_id=repo_id,
                repo_url=repo_url,
                analysis_type=analysis_type,
                name=results.get("repository_name", ""),
                description=results.get("description", "")
            )
            
            # Store modules and their relationships
            if "modules" in results:
                for module in results["modules"]:
                    session.run(
                        """
                        MATCH (r:Repository {id: $repo_id})
                        MERGE (m:Module {name: $module_name, repository_id: $repo_id})
                        SET m.path = $path,
                            m.type = $type,
                            m.complexity = $complexity,
                            m.lines_of_code = $loc
                        MERGE (r)-[:CONTAINS]->(m)
                        """,
                        repo_id=repo_id,
                        module_name=module.get("name", ""),
                        path=module.get("path", ""),
                        type=module.get("type", ""),
                        complexity=module.get("complexity", 0),
                        loc=module.get("lines_of_code", 0)
                    )
            
            # Store dependencies
            if "dependencies" in results:
                for dep in results["dependencies"]:
                    session.run(
                        """
                        MATCH (r:Repository {id: $repo_id})
                        MERGE (d:Dependency {name: $dep_name})
                        SET d.version = $version,
                            d.type = $type
                        MERGE (r)-[:DEPENDS_ON]->(d)
                        """,
                        repo_id=repo_id,
                        dep_name=dep.get("name", ""),
                        version=dep.get("version", ""),
                        type=dep.get("type", "")
                    )
    
    async def _store_in_weaviate(
        self,
        repo_id: str,
        repo_url: str,
        results: Dict[str, Any]
    ):
        """Store vector embeddings in Weaviate"""
        if not self.weaviate_client:
            return
        
        try:
            # Create schema if it doesn't exist
            self._ensure_weaviate_schema()
            
            # Store repository summary
            if "summary" in results:
                self.weaviate_client.data_object.create(
                    data_object={
                        "repository_id": repo_id,
                        "repository_url": repo_url,
                        "content": results["summary"],
                        "type": "summary",
                        "timestamp": datetime.now().isoformat()
                    },
                    class_name="RepositoryContent"
                )
            
            # Store module documentation
            if "modules" in results:
                for module in results["modules"]:
                    if "documentation" in module:
                        self.weaviate_client.data_object.create(
                            data_object={
                                "repository_id": repo_id,
                                "repository_url": repo_url,
                                "content": module["documentation"],
                                "type": "module_doc",
                                "module_name": module.get("name", ""),
                                "module_path": module.get("path", ""),
                                "timestamp": datetime.now().isoformat()
                            },
                            class_name="RepositoryContent"
                        )
            
        except Exception as e:
            logger.error(f"Error storing in Weaviate: {e}")
    
    def _ensure_weaviate_schema(self):
        """Ensure Weaviate schema exists"""
        if not self.weaviate_client:
            return
        
        schema = {
            "class": "RepositoryContent",
            "description": "Repository analysis content for RAG",
            "properties": [
                {
                    "name": "repository_id",
                    "dataType": ["string"],
                    "description": "Repository identifier"
                },
                {
                    "name": "repository_url",
                    "dataType": ["string"],
                    "description": "Repository URL"
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Content for semantic search"
                },
                {
                    "name": "type",
                    "dataType": ["string"],
                    "description": "Content type (summary, module_doc, etc.)"
                },
                {
                    "name": "module_name",
                    "dataType": ["string"],
                    "description": "Module name if applicable"
                },
                {
                    "name": "module_path",
                    "dataType": ["string"],
                    "description": "Module path if applicable"
                },
                {
                    "name": "timestamp",
                    "dataType": ["string"],
                    "description": "Creation timestamp"
                }
            ],
            "vectorizer": "text2vec-openai"
        }
        
        try:
            if not self.weaviate_client.schema.exists("RepositoryContent"):
                self.weaviate_client.schema.create_class(schema)
        except Exception as e:
            logger.error(f"Error creating Weaviate schema: {e}")
    
    async def get_all_repositories(self) -> List[Dict[str, Any]]:
        """Get all analyzed repositories"""
        repositories = []
        
        if self.neo4j_driver:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    """
                    MATCH (r:Repository)
                    RETURN r.id as id, r.url as url, r.name as name,
                           r.description as description, r.last_analyzed as last_analyzed,
                           r.analysis_type as analysis_type
                    ORDER BY r.last_analyzed DESC
                    """
                )
                
                for record in result:
                    repositories.append({
                        "id": record["id"],
                        "url": record["url"],
                        "name": record["name"],
                        "description": record["description"],
                        "last_analyzed": record["last_analyzed"],
                        "analysis_type": record["analysis_type"]
                    })
        
        return repositories
    
    async def get_repository_insights(self, repo_id: str) -> Dict[str, Any]:
        """Get insights for a specific repository"""
        insights = {}
        
        if self.neo4j_driver:
            with self.neo4j_driver.session() as session:
                # Get repository info
                repo_result = session.run(
                    "MATCH (r:Repository {id: $repo_id}) RETURN r",
                    repo_id=repo_id
                )
                repo_record = repo_result.single()
                if repo_record:
                    insights["repository"] = dict(repo_record["r"])
                
                # Get module count and complexity
                module_result = session.run(
                    """
                    MATCH (r:Repository {id: $repo_id})-[:CONTAINS]->(m:Module)
                    RETURN count(m) as module_count,
                           avg(m.complexity) as avg_complexity,
                           sum(m.lines_of_code) as total_loc
                    """,
                    repo_id=repo_id
                )
                module_record = module_result.single()
                if module_record:
                    insights["metrics"] = {
                        "module_count": module_record["module_count"],
                        "avg_complexity": module_record["avg_complexity"],
                        "total_lines_of_code": module_record["total_loc"]
                    }
                
                # Get dependencies
                dep_result = session.run(
                    """
                    MATCH (r:Repository {id: $repo_id})-[:DEPENDS_ON]->(d:Dependency)
                    RETURN d.name as name, d.version as version, d.type as type
                    """,
                    repo_id=repo_id
                )
                insights["dependencies"] = [
                    {
                        "name": record["name"],
                        "version": record["version"],
                        "type": record["type"]
                    }
                    for record in dep_result
                ]
        
        return insights
    
    async def delete_repository(self, repo_id: str):
        """Delete repository and all associated data"""
        if self.neo4j_driver:
            with self.neo4j_driver.session() as session:
                session.run(
                    """
                    MATCH (r:Repository {id: $repo_id})
                    DETACH DELETE r
                    """,
                    repo_id=repo_id
                )
        
        if self.weaviate_client:
            try:
                self.weaviate_client.data_object.delete_many(
                    class_name="RepositoryContent",
                    where={
                        "path": ["repository_id"],
                        "operator": "Equal",
                        "valueString": repo_id
                    }
                )
            except Exception as e:
                logger.error(f"Error deleting from Weaviate: {e}")
    
    def _generate_repo_id(self, repo_url: str) -> str:
        """Generate a unique repository ID from URL"""
        return hashlib.md5(repo_url.encode()).hexdigest()
    
    def close(self):
        """Close database connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()