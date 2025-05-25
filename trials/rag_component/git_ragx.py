"""
GitHub Repository RAG Pipeline with FAISS

A comprehensive RAG (Retrieval Augmented Generation) pipeline specifically designed
for GitHub repositories using FAISS for efficient vector search and smart chunking
strategies optimized for code analysis.
"""

import os
import re
import ast
import json
import logging
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import pickle
from urllib.parse import urlparse

try:
    import faiss
except ImportError:
    print("FAISS not installed. Run: pip install faiss-cpu")
    faiss = None

try:
    import numpy as np
except ImportError:
    print("NumPy not installed. Run: pip install numpy")
    np = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("SentenceTransformers not installed. Run: pip install sentence-transformers")
    SentenceTransformer = None

try:
    import git
except ImportError:
    print("GitPython not installed. Run: pip install GitPython")
    git = None

try:
    from github import Github
except ImportError:
    print("PyGithub not installed. Run: pip install PyGithub")
    Github = None

try:
    from transformers import AutoTokenizer
except ImportError:
    print("Transformers not installed. Run: pip install transformers")
    AutoTokenizer = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""
    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # 'function', 'class', 'module', 'comment', 'mixed'
    language: str
    size: int
    hash_id: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.embedding is not None:
            data['embedding'] = self.embedding.tolist()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeChunk':
        """Create from dictionary."""
        if 'embedding' in data and data['embedding'] is not None:
            data['embedding'] = np.array(data['embedding'])
        return cls(**data)


class GitHubRepoManager:
    """Manages GitHub repository operations."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.github_client = None
        
        if self.github_token and Github:
            try:
                self.github_client = Github(self.github_token)
                logger.info("GitHub client initialized with token")
            except Exception as e:
                logger.warning(f"Failed to initialize GitHub client: {e}")
    
    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        # Handle various GitHub URL formats
        url = url.strip().rstrip('/')
        
        # Remove .git suffix if present
        if url.endswith('.git'):
            url = url[:-4]
        
        # Parse URL
        if url.startswith('https://github.com/'):
            parts = url.replace('https://github.com/', '').split('/')
        elif url.startswith('git@github.com:'):
            parts = url.replace('git@github.com:', '').split('/')
        else:
            raise ValueError(f"Invalid GitHub URL format: {url}")
        
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL format: {url}")
        
        owner, repo = parts[0], parts[1]
        return owner, repo
    
    def get_repo_info(self, github_url: str) -> Dict[str, Any]:
        """Get repository information from GitHub API."""
        if not self.github_client:
            return {}
        
        try:
            owner, repo_name = self.parse_github_url(github_url)
            repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'language': repo.language,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'size': repo.size,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                'topics': repo.get_topics(),
                'default_branch': repo.default_branch
            }
        except Exception as e:
            logger.warning(f"Could not fetch repo info: {e}")
            return {}
    
    def clone_repository(self, github_url: str, target_dir: Path) -> bool:
        """Clone GitHub repository to local directory."""
        if not git:
            logger.error("GitPython not available for cloning")
            return False
        
        try:
            # Ensure target directory exists and is empty
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone repository
            logger.info(f"Cloning repository from {github_url}...")
            git.Repo.clone_from(github_url, target_dir, depth=1)  # Shallow clone
            logger.info(f"Repository cloned to {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            return False


class SmartCodeChunker:
    """Smart chunking strategy optimized for code analysis."""
    
    def __init__(self, 
                 max_chunk_size: int = 1000,
                 overlap_size: int = 100,
                 min_chunk_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        
        # Language-specific patterns
        self.language_patterns = {
            'python': {
                'function': r'^\s*def\s+\w+\s*\(',
                'class': r'^\s*class\s+\w+\s*[\(:]',
                'import': r'^\s*(?:from\s+\S+\s+)?import\s+',
                'comment': r'^\s*#',
                'docstring': r'\s*"""[\s\S]*?"""',
            },
            'javascript': {
                'function': r'^\s*(?:function\s+\w+|\w+\s*[:=]\s*function|\w+\s*=>)',
                'class': r'^\s*class\s+\w+',
                'import': r'^\s*(?:import|export|require)\s+',
                'comment': r'^\s*//',
            },
            'java': {
                'function': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\(',
                'class': r'^\s*(?:public|private)?\s*class\s+\w+',
                'import': r'^\s*import\s+',
                'comment': r'^\s*//',
            },
            'cpp': {
                'function': r'^\s*(?:\w+\s+)*\w+\s*\([^)]*\)\s*{',
                'class': r'^\s*class\s+\w+',
                'include': r'^\s*#include\s*[<"]',
                'comment': r'^\s*//',
            }
        }
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
        }
        return language_map.get(ext, 'text')
    
    def extract_ast_chunks(self, content: str, file_path: str) -> List[CodeChunk]:
        """Extract chunks based on AST analysis (Python only)."""
        chunks = []
        language = self.detect_language(file_path)
        
        if language == 'python':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                        start_line = node.lineno
                        end_line = getattr(node, 'end_lineno', start_line)
                        
                        lines = content.split('\n')
                        chunk_content = '\n'.join(lines[start_line-1:end_line])
                        
                        chunk_type = 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class'
                        
                        chunk = CodeChunk(
                            content=chunk_content,
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line,
                            chunk_type=chunk_type,
                            language=language,
                            size=len(chunk_content),
                            hash_id=hashlib.md5(chunk_content.encode()).hexdigest(),
                            metadata={
                                'name': node.name,
                                'type': chunk_type,
                                'docstring': ast.get_docstring(node)
                            }
                        )
                        chunks.append(chunk)
            except SyntaxError:
                logger.warning(f"Could not parse {file_path} as Python code")
        
        return chunks
    
    def extract_regex_chunks(self, content: str, file_path: str) -> List[CodeChunk]:
        """Extract chunks using regex patterns."""
        chunks = []
        language = self.detect_language(file_path)
        patterns = self.language_patterns.get(language, {})
        
        lines = content.split('\n')
        current_chunk = []
        current_start = 1
        current_type = 'mixed'
        
        for i, line in enumerate(lines, 1):
            # Check if line matches any pattern
            line_type = 'code'
            for pattern_type, pattern in patterns.items():
                if re.match(pattern, line):
                    line_type = pattern_type
                    break
            
            # If we hit a function/class definition and have accumulated content
            if line_type in ['function', 'class'] and current_chunk:
                # Create chunk from accumulated content
                chunk_content = '\n'.join(current_chunk)
                if len(chunk_content.strip()) >= self.min_chunk_size:
                    chunk = CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=current_start,
                        end_line=i-1,
                        chunk_type=current_type,
                        language=language,
                        size=len(chunk_content),
                        hash_id=hashlib.md5(chunk_content.encode()).hexdigest(),
                        metadata={'extracted_by': 'regex'}
                    )
                    chunks.append(chunk)
                
                # Start new chunk
                current_chunk = [line]
                current_start = i
                current_type = line_type
            else:
                current_chunk.append(line)
                if line_type != 'code' and current_type == 'mixed':
                    current_type = line_type
            
            # If chunk gets too large, split it
            if len('\n'.join(current_chunk)) > self.max_chunk_size:
                chunk_content = '\n'.join(current_chunk)
                chunk = CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_start,
                    end_line=i,
                    chunk_type=current_type,
                    language=language,
                    size=len(chunk_content),
                    hash_id=hashlib.md5(chunk_content.encode()).hexdigest(),
                    metadata={'extracted_by': 'regex', 'split_reason': 'size_limit'}
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-self.overlap_size//20:] if len(current_chunk) > self.overlap_size//20 else current_chunk
                current_chunk = overlap_lines
                current_start = i - len(overlap_lines) + 1
                current_type = 'mixed'
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) >= self.min_chunk_size:
                chunk = CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_start,
                    end_line=len(lines),
                    chunk_type=current_type,
                    language=language,
                    size=len(chunk_content),
                    hash_id=hashlib.md5(chunk_content.encode()).hexdigest(),
                    metadata={'extracted_by': 'regex'}
                )
                chunks.append(chunk)
        
        return chunks
    
    def chunk_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk a file using the best available strategy."""
        language = self.detect_language(file_path)
        
        # Try AST-based chunking for Python
        if language == 'python':
            ast_chunks = self.extract_ast_chunks(content, file_path)
            if ast_chunks:
                return ast_chunks
        
        # Fall back to regex-based chunking
        return self.extract_regex_chunks(content, file_path)


class GitHubRAGPipeline:
    """Main RAG pipeline for GitHub repositories with FAISS indexing."""
    
    def __init__(self,
                 github_url: str,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 cache_dir: Optional[str] = None,
                 chunk_size: int = 1000,
                 overlap_size: int = 100,
                 github_token: Optional[str] = None):
        
        self.github_url = github_url
        self.embedding_model_name = embedding_model
        self.github_token = github_token
        
        # Initialize components first
        self.github_manager = GitHubRepoManager(github_token)
        self.chunker = SmartCodeChunker(chunk_size, overlap_size)
        
        # Setup directories (now that github_manager exists)
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Create cache directory based on repo name
            owner, repo_name = self._parse_github_url(github_url)
            self.cache_dir = Path.home() / ".github_rag_cache" / f"{owner}_{repo_name}"
        
        self.repo_dir = self.cache_dir / "repository"
        self.index_path = self.cache_dir / "index"
        
        # Initialize remaining attributes
        self.chunks: List[CodeChunk] = []
        self.index = None
        self.embedding_model = None
        self.repo_info = {}
        
        # File filters
        self.include_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.cs', '.scala', '.kt', '.swift', '.dart',
            '.md', '.txt', '.yml', '.yaml', '.json', '.xml', '.html', '.css', '.sql'
        }
        
        self.exclude_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.DS_Store',
            'target', 'bin', 'obj', '.gradle', '.idea', '.vscode'
        }
        
        # Initialize
        self._setup_directories()
        self._load_embedding_model()
    
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        return self.github_manager.parse_github_url(url)
    
    def _setup_directories(self):
        """Setup cache directories."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path.mkdir(exist_ok=True)
        (self.index_path / "chunks").mkdir(exist_ok=True)
        (self.index_path / "embeddings").mkdir(exist_ok=True)
    
    def _load_embedding_model(self):
        """Load the sentence transformer model."""
        if SentenceTransformer is None:
            logger.error("SentenceTransformers not available")
            return
        
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Loaded embedding model: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in processing (debug version)."""
        # Only exclude obvious binary/cache directories
        path_str = str(file_path).lower()
        if any(exclude in path_str for exclude in ['__pycache__', 'node_modules', '.git/', 'dist/', 'build/', '.venv/', 'venv/']):
            return False
        
        # Skip very large files
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                return False
        except OSError:
            return False
        
        # Include almost everything else
        return True
    
    def clone_and_extract_files(self) -> List[Tuple[str, str]]:
        """Clone repository and extract all relevant files."""
        # Clone repository if not already cloned
        if not self.repo_dir.exists() or not any(self.repo_dir.iterdir()):
            success = self.github_manager.clone_repository(self.github_url, self.repo_dir)
            if not success:
                logger.error("Failed to clone repository")
                return []
        
        # Get repository info
        self.repo_info = self.github_manager.get_repo_info(self.github_url)
        
        # Extract files
        files = []
        for file_path in self.repo_dir.rglob('*'):
            if file_path.is_file() and self._should_include_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    relative_path = str(file_path.relative_to(self.repo_dir))
                    files.append((relative_path, content))
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        logger.info(f"Extracted {len(files)} files from repository")
        return files
    
    def process_repository(self, force_rebuild: bool = False) -> None:
        """Process the entire repository and build the index."""
        cache_file = self.index_path / "chunks" / "chunks.pkl"
        
        # Load from cache if available and not forcing rebuild
        if not force_rebuild and cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    chunk_data = pickle.load(f)
                self.chunks = [CodeChunk.from_dict(data) for data in chunk_data]
                logger.info(f"Loaded {len(self.chunks)} chunks from cache")
                self._load_or_build_index()
                return
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        
        # Extract and chunk files
        files = self.clone_and_extract_files()
        self.chunks = []
        
        for file_path, content in files:
            try:
                file_chunks = self.chunker.chunk_file(file_path, content)
                self.chunks.extend(file_chunks)
            except Exception as e:
                logger.warning(f"Could not chunk {file_path}: {e}")
        
        logger.info(f"Created {len(self.chunks)} chunks from {len(files)} files")
        
        # Generate embeddings
        self._generate_embeddings()
        
        # Build FAISS index
        self._build_faiss_index()
        
        # Save to cache
        self._save_cache()
    
    def _generate_embeddings(self):
        """Generate embeddings for all chunks."""
        if self.embedding_model is None:
            logger.error("Embedding model not available")
            return
        
        logger.info("Generating embeddings...")
        
        # Prepare texts for embedding
        texts = []
        for chunk in self.chunks:
            # Create rich text representation
            text = f"Repository: {self.repo_info.get('full_name', 'Unknown')}\n"
            text += f"File: {chunk.file_path}\n"
            text += f"Type: {chunk.chunk_type}\n"
            text += f"Language: {chunk.language}\n"
            if chunk.metadata.get('name'):
                text += f"Name: {chunk.metadata['name']}\n"
            text += f"Content:\n{chunk.content}"
            texts.append(text)
        
        # Generate embeddings in batches
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)
            
            for j, embedding in enumerate(batch_embeddings):
                self.chunks[i+j].embedding = embedding
        
        logger.info(f"Generated embeddings for {len(self.chunks)} chunks")
    
    def _build_faiss_index(self):
        """Build FAISS index from embeddings."""
        if faiss is None or np is None:
            logger.error("FAISS or NumPy not available")
            return
        
        # Get embeddings
        embeddings = np.array([chunk.embedding for chunk in self.chunks if chunk.embedding is not None])
        
        if len(embeddings) == 0:
            logger.error("No embeddings available for indexing")
            return
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def _load_or_build_index(self):
        """Load existing FAISS index or build new one."""
        index_file = self.index_path / "embeddings" / "faiss.index"
        
        if index_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Could not load FAISS index: {e}")
        
        # Build new index
        self._build_faiss_index()
    
    def _save_cache(self):
        """Save chunks and index to cache."""
        # Save chunks
        chunk_data = [chunk.to_dict() for chunk in self.chunks]
        with open(self.index_path / "chunks" / "chunks.pkl", 'wb') as f:
            pickle.dump(chunk_data, f)
        
        # Save repository info
        with open(self.index_path / "repo_info.json", 'w') as f:
            json.dump(self.repo_info, f, indent=2)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path / "embeddings" / "faiss.index"))
        
        logger.info("Saved cache")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[CodeChunk, float]]:
        """Search for relevant code chunks."""
        if self.embedding_model is None or self.index is None:
            logger.error("Search not available - missing components")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def get_repository_summary(self) -> Dict[str, Any]:
        """Get a summary of the repository structure."""
        summary = {
            'repository_info': self.repo_info,
            'total_chunks': len(self.chunks),
            'languages': {},
            'chunk_types': {},
            'files': set(),
            'total_size': 0
        }
        
        for chunk in self.chunks:
            # Count languages
            summary['languages'][chunk.language] = summary['languages'].get(chunk.language, 0) + 1
            
            # Count chunk types
            summary['chunk_types'][chunk.chunk_type] = summary['chunk_types'].get(chunk.chunk_type, 0) + 1
            
            # Track files
            summary['files'].add(chunk.file_path)
            
            # Sum sizes
            summary['total_size'] += chunk.size
        
        summary['files'] = len(summary['files'])
        return summary
    
    def query_repository(self, query: str, top_k: int = 5, include_context: bool = True) -> str:
        """Query the repository and return a formatted response."""
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant code found for your query."
        
        response = f"# Query Results for: '{query}'\n\n"
        response += f"**Repository:** {self.repo_info.get('full_name', 'Unknown')}\n"
        if self.repo_info.get('description'):
            response += f"**Description:** {self.repo_info['description']}\n"
        response += f"\nFound {len(results)} relevant code chunks:\n\n"
        
        for i, (chunk, score) in enumerate(results, 1):
            response += f"## Result {i} (Relevance: {score:.3f})\n"
            response += f"**File:** `{chunk.file_path}`\n"
            response += f"**Type:** {chunk.chunk_type} ({chunk.language})\n"
            response += f"**Lines:** {chunk.start_line}-{chunk.end_line}\n"
            response += f"**Lines:** {chunk.start_line}-{chunk.end_line}\n"
            
            if chunk.metadata.get('name'):
                response += f"**Name:** {chunk.metadata['name']}\n"
            
            response += "\n```" + chunk.language + "\n"
            response += chunk.content
            response += "\n```\n\n"
            
            if include_context and chunk.metadata.get('docstring'):
                response += f"**Documentation:** {chunk.metadata['docstring']}\n\n"
        
        return response


def main():
    """Example usage of the GitHubRAGPipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Repository RAG Pipeline')
    parser.add_argument('github_url', help='GitHub repository URL')
    parser.add_argument('--query', '-q', help='Query to search for')
    parser.add_argument('--rebuild', '-r', action='store_true', help='Force rebuild index')
    parser.add_argument('--cache-dir', help='Custom cache directory')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    parser.add_argument('--github-token', help='GitHub API token')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = GitHubRAGPipeline(
        github_url=args.github_url,
        cache_dir=args.cache_dir,
        github_token=args.github_token
    )
    
    try:
        # Process repository
        print(f"Processing repository: {args.github_url}")
        pipeline.process_repository(force_rebuild=args.rebuild)
        
        # Show summary
        summary = pipeline.get_repository_summary()
        print(f"\nRepository Summary:")
        print(f"- Total chunks: {summary['total_chunks']}")
        print(f"- Files processed: {summary['files']}")
        print(f"- Languages: {', '.join(summary['languages'].keys())}")
        print(f"- Total size: {summary['total_size']:,} characters")
        
        # Interactive query mode if no query provided
        if args.query:
            print(f"\nSearching for: {args.query}")
            result = pipeline.query_repository(args.query, top_k=args.top_k)
            print(result)
        else:
            print("\nEntering interactive query mode. Type 'quit' to exit.")
            while True:
                query = input("\nEnter your query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query:
                    result = pipeline.query_repository(query, top_k=args.top_k)
                    print(result)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()


def _should_include_file(self, file_path: Path) -> bool:
    """Check if file should be included in processing."""
    # Skip hidden files and directories (but allow some config files)
    if any(part.startswith('.') for part in file_path.parts):
        allowed_hidden = {'.gitignore', '.env.example', '.dockerignore', '.github'}
        if not any(allowed in str(file_path) for allowed in allowed_hidden):
            return False
    
    # More specific exclude patterns
    path_str = str(file_path).lower()
    strict_exclude = {
        '__pycache__', 'node_modules', '.pytest_cache', '.mypy_cache',
        'dist/', 'build/', 'target/', 'bin/', 'obj/', '.gradle/'
    }
    
    if any(pattern in path_str for pattern in strict_exclude):
        return False
    
    # Much more inclusive file extensions
    include_extensions = {
        # Programming languages
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.cs', '.scala', '.kt', '.swift', '.dart',
        '.html', '.css', '.scss', '.less', '.vue', '.svelte',
        # Documentation and config
        '.md', '.txt', '.rst', '.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.cfg',
        '.dockerfile', '.sh', '.bat', '.ps1',
        # Data files
        '.sql', '.csv', '.tsv',
        # No extension (often important files like Makefile, Dockerfile, etc.)
        ''
    }
    
    file_ext = file_path.suffix.lower()
    
    # Include if extension matches OR if it's a file without extension
    if file_ext in include_extensions or (not file_ext and file_path.is_file()):
        # Increase file size limit to 10MB
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except OSError:
            return False
        return True
    
    return False