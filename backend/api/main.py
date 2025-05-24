from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

from backend.agents.agents import get_crew
from backend.services.memory_service import MemoryService
from backend.services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Repository Analysis API",
    description="AI-powered repository analysis and insights platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RepositoryAnalysisRequest(BaseModel):
    repo_url: HttpUrl
    analysis_type: Optional[str] = "full"  # full, quick, architecture, security
    include_docs: Optional[bool] = True
    include_tests: Optional[bool] = True

class ChatRequest(BaseModel):
    message: str
    repo_url: Optional[HttpUrl] = None
    context: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    repo_url: str
    created_at: datetime
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None

# Global services
memory_service = MemoryService()
rag_service = RAGService()

# In-memory storage for demo (replace with proper database)
analysis_jobs = {}

@app.get("/")
async def root():
    return {"message": "Repository Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: RepositoryAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start repository analysis"""
    try:
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create analysis job
        analysis_job = AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            repo_url=str(request.repo_url),
            created_at=datetime.now()
        )
        
        analysis_jobs[analysis_id] = analysis_job
        
        # Start background analysis
        background_tasks.add_task(
            run_analysis,
            analysis_id,
            str(request.repo_url),
            request.analysis_type,
            request.include_docs,
            request.include_tests
        )
        
        return analysis_job
        
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(analysis_id: str):
    """Get analysis status and results"""
    if analysis_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_jobs[analysis_id]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_repo(
    request: ChatRequest
):
    """Chat with repository using RAG"""
    try:
        # Use RAG service to get context-aware response
        response = await rag_service.query(
            query=request.message,
            repo_url=str(request.repo_url) if request.repo_url else None,
            context=request.context
        )
        
        return ChatResponse(
            response=response["answer"],
            sources=response.get("sources", []),
            context=response.get("context", {})
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repositories")
async def list_analyzed_repositories():
    """List all analyzed repositories"""
    try:
        repositories = await memory_service.get_all_repositories()
        return {"repositories": repositories}
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/repositories/{repo_id}/insights")
async def get_repository_insights(repo_id: str):
    """Get insights for a specific repository"""
    try:
        insights = await memory_service.get_repository_insights(repo_id)
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/repositories/{repo_id}")
async def delete_repository(repo_id: str):
    """Delete repository and its analysis data"""
    try:
        await memory_service.delete_repository(repo_id)
        return {"message": "Repository deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting repository: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis(
    analysis_id: str,
    repo_url: str,
    analysis_type: str,
    include_docs: bool,
    include_tests: bool
):
    """Background task to run repository analysis"""
    try:
        logger.info(f"Starting analysis {analysis_id} for {repo_url}")
        
        # Update status
        analysis_jobs[analysis_id].status = "running"
        
        # Get CrewAI crew and run analysis
        crew = get_crew()
        
        # Prepare inputs for the crew
        inputs = {
            "repo_url": repo_url,
            "analysis_type": analysis_type,
            "include_docs": include_docs,
            "include_tests": include_tests
        }
        
        # Run the crew
        result = crew.kickoff(inputs=inputs)
        
        # Store results in memory service
        await memory_service.store_analysis_results(
            repo_url=repo_url,
            results=result,
            analysis_type=analysis_type
        )
        
        # Update analysis job with results
        analysis_jobs[analysis_id].status = "completed"
        analysis_jobs[analysis_id].results = result
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in analysis {analysis_id}: {str(e)}")
        analysis_jobs[analysis_id].status = "failed"
        analysis_jobs[analysis_id].error = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)