import os
import logging
from typing import Dict, List, Any, Optional
import openai
from datetime import datetime

try:
    import weaviate
except ImportError:
    weaviate = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)

class RAGService:
    """Service for Retrieval-Augmented Generation using repository knowledge"""
    
    def __init__(self):
        self.weaviate_client = None
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI and vector database clients"""
        # Weaviate client
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
                logger.info("RAG Service connected to Weaviate")
            except Exception as e:
                logger.warning(f"Failed to connect to Weaviate: {e}")
        
        # OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            logger.info("RAG Service connected to OpenAI")
        
        # Anthropic client
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key and Anthropic:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
            logger.info("RAG Service connected to Anthropic")
    
    async def query(
        self,
        query: str,
        repo_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Query repository knowledge using RAG"""
        try:
            # Retrieve relevant context
            relevant_docs = await self._retrieve_context(
                query=query,
                repo_url=repo_url,
                max_results=max_results
            )
            
            # Generate response using retrieved context
            response = await self._generate_response(
                query=query,
                context_docs=relevant_docs,
                additional_context=context
            )
            
            return {
                "answer": response,
                "sources": relevant_docs,
                "context": {
                    "query": query,
                    "repo_url": repo_url,
                    "timestamp": datetime.now().isoformat(),
                    "num_sources": len(relevant_docs)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your query. Please try again.",
                "sources": [],
                "context": {"error": str(e)}
            }
    
    async def _retrieve_context(
        self,
        query: str,
        repo_url: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from vector database"""
        if not self.weaviate_client:
            logger.warning("Weaviate client not available for context retrieval")
            return []
        
        try:
            # Build where filter
            where_filter = None
            if repo_url:
                repo_id = self._generate_repo_id(repo_url)
                where_filter = {
                    "path": ["repository_id"],
                    "operator": "Equal",
                    "valueString": repo_id
                }
            
            # Perform semantic search
            result = (
                self.weaviate_client.query
                .get("RepositoryContent", [
                    "repository_id",
                    "repository_url", 
                    "content",
                    "type",
                    "module_name",
                    "module_path",
                    "timestamp"
                ])
                .with_near_text({"concepts": [query]})
                .with_limit(max_results)
                .with_additional(["score"])
            )
            
            if where_filter:
                result = result.with_where(where_filter)
            
            response = result.do()
            
            # Process results
            documents = []
            if "data" in response and "Get" in response["data"]:
                for item in response["data"]["Get"]["RepositoryContent"]:
                    documents.append({
                        "content": item.get("content", ""),
                        "type": item.get("type", ""),
                        "module_name": item.get("module_name", ""),
                        "module_path": item.get("module_path", ""),
                        "repository_url": item.get("repository_url", ""),
                        "score": item.get("_additional", {}).get("score", 0),
                        "timestamp": item.get("timestamp", "")
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    async def _generate_response(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response using LLM with retrieved context"""
        # Prepare context string
        context_str = self._format_context(context_docs, additional_context)
        
        # Create prompt
        prompt = self._create_prompt(query, context_str)
        
        # Generate response using available LLM
        if self.anthropic_client:
            return await self._generate_with_anthropic(prompt)
        elif self.openai_client:
            return await self._generate_with_openai(prompt)
        else:
            return "I apologize, but no language model is currently available to process your query."
    
    def _format_context(
        self,
        context_docs: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format retrieved documents into context string"""
        if not context_docs:
            return "No relevant repository information found."
        
        context_parts = []
        
        for i, doc in enumerate(context_docs, 1):
            doc_info = f"Document {i}:"
            if doc.get("type"):
                doc_info += f" (Type: {doc['type']})"
            if doc.get("module_name"):
                doc_info += f" (Module: {doc['module_name']})"
            if doc.get("module_path"):
                doc_info += f" (Path: {doc['module_path']})"
            
            context_parts.append(f"{doc_info}\n{doc.get('content', '')}")
        
        context_str = "\n\n".join(context_parts)
        
        if additional_context:
            context_str += f"\n\nAdditional Context: {additional_context}"
        
        return context_str
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM"""
        return f"""You are an AI assistant specialized in repository analysis and code understanding. 
You have access to repository documentation and analysis results.

Context from repository analysis:
{context}

User Question: {query}

Please provide a helpful and accurate response based on the repository context provided. 
If the context doesn't contain enough information to fully answer the question, 
please say so and provide what information you can based on the available context.

Response:"""
    
    async def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate response using Anthropic Claude"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error with Anthropic: {e}")
            return "I encountered an error while generating a response. Please try again."
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in repository analysis and code understanding."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error with OpenAI: {e}")
            return "I encountered an error while generating a response. Please try again."
    
    def _generate_repo_id(self, repo_url: str) -> str:
        """Generate repository ID from URL"""
        import hashlib
        return hashlib.md5(repo_url.encode()).hexdigest()
    
    async def get_repository_summary(self, repo_url: str) -> Dict[str, Any]:
        """Get a summary of repository analysis"""
        try:
            # Retrieve summary documents
            summary_docs = await self._retrieve_context(
                query="repository summary overview architecture",
                repo_url=repo_url,
                max_results=3
            )
            
            # Filter for summary type documents
            summary_content = []
            for doc in summary_docs:
                if doc.get("type") == "summary":
                    summary_content.append(doc["content"])
            
            if summary_content:
                return {
                    "summary": "\n\n".join(summary_content),
                    "last_updated": summary_docs[0].get("timestamp", ""),
                    "repository_url": repo_url
                }
            else:
                return {
                    "summary": "No summary available for this repository.",
                    "repository_url": repo_url
                }
                
        except Exception as e:
            logger.error(f"Error getting repository summary: {e}")
            return {
                "summary": "Error retrieving repository summary.",
                "error": str(e),
                "repository_url": repo_url
            }