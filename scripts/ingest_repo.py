#!/usr/bin/env python3
"""
Repository Ingestion CLI

Command-line interface for ingesting GitHub repositories into the vector search system.

Usage:
    python scripts/ingest_repo.py <github_url> [options]
    python scripts/ingest_repo.py --batch <file_with_urls> [options]

Examples:
    # Ingest a single repository
    python scripts/ingest_repo.py https://github.com/owner/repo
    
    # Ingest multiple repositories from a file
    python scripts/ingest_repo.py --batch repos.txt
    
    # Ingest with custom chunk size
    python scripts/ingest_repo.py https://github.com/owner/repo --chunk-size 1500
    
    # Ingest with progress output
    python scripts/ingest_repo.py https://github.com/owner/repo --verbose
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.ingestion.pipeline import IngestionPipeline
from backend.ingestion.models import ProcessingResult
from backend.services.google_vector_search_service import GoogleVectorSearchService
from backend.core.logging import RepoAnalysisLogger

logger = RepoAnalysisLogger(__name__)


class IngestionCLI:
    """Command-line interface for repository ingestion."""
    
    def __init__(self):
        self.vector_service = None
        self.pipeline = None
        self.verbose = False
    
    async def initialize_services(self) -> bool:
        """Initialize the vector search service and pipeline."""
        try:
            # Initialize Google Vector Search service
            self.vector_service = GoogleVectorSearchService()
            await self.vector_service.initialize()
            
            # Initialize ingestion pipeline
            github_token = os.getenv('GITHUB_TOKEN')
            
            progress_callback = self._progress_callback if self.verbose else None
            
            self.pipeline = IngestionPipeline(
                vector_service=self.vector_service,
                github_token=github_token,
                progress_callback=progress_callback
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            return False
    
    def _progress_callback(self, message: str, percentage: float) -> None:
        """Progress callback for verbose output."""
        if self.verbose:
            print(f"\r[{percentage:3.0f}%] {message}", end="", flush=True)
            if percentage >= 100:
                print()  # New line when complete
    
    async def ingest_single_repository(self, repo_url: str) -> ProcessingResult:
        """Ingest a single repository."""
        print(f"\n🚀 Starting ingestion of: {repo_url}")
        
        result = await self.pipeline.process_repository(repo_url)
        
        if result.success:
            print(f"\n✅ Successfully ingested {repo_url}")
            print(f"   📊 Statistics:")
            print(f"      • Files processed: {result.repo_metadata.processed_files}")
            print(f"      • Chunks created: {result.chunks_created}")
            print(f"      • Chunks embedded: {result.chunks_embedded}")
            print(f"      • Chunks stored: {result.chunks_stored}")
            print(f"      • Processing time: {result.processing_time_seconds:.2f}s")
            print(f"      • Languages: {', '.join(result.repo_metadata.languages)}")
        else:
            print(f"\n❌ Failed to ingest {repo_url}")
            print(f"   Error: {result.error_message}")
            if result.warnings:
                print(f"   Warnings: {', '.join(result.warnings)}")
        
        return result
    
    async def ingest_multiple_repositories(self, repo_urls: List[str]) -> List[ProcessingResult]:
        """Ingest multiple repositories."""
        print(f"\n🚀 Starting batch ingestion of {len(repo_urls)} repositories")
        
        results = await self.pipeline.process_multiple_repositories(repo_urls)
        
        # Print summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"\n📊 Batch Ingestion Summary:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if successful:
            total_chunks = sum(r.chunks_stored for r in successful)
            total_time = sum(r.processing_time_seconds for r in successful)
            print(f"   📈 Total chunks stored: {total_chunks}")
            print(f"   ⏱️  Total processing time: {total_time:.2f}s")
        
        if failed:
            print(f"\n❌ Failed repositories:")
            for result in failed:
                print(f"   • {result.repo_metadata.url}: {result.error_message}")
        
        return results
    
    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load repository URLs from a file."""
        try:
            with open(file_path, 'r') as f:
                urls = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
                return urls
        except Exception as e:
            logger.error(f"Failed to load URLs from {file_path}: {str(e)}")
            return []
    
    def save_results_to_file(self, results: List[ProcessingResult], output_file: str) -> None:
        """Save processing results to a JSON file."""
        try:
            results_data = []
            for result in results:
                result_dict = {
                    "repo_url": result.repo_metadata.url,
                    "repo_id": result.repo_metadata.repo_id,
                    "success": result.success,
                    "chunks_created": result.chunks_created,
                    "chunks_embedded": result.chunks_embedded,
                    "chunks_stored": result.chunks_stored,
                    "processing_time_seconds": result.processing_time_seconds,
                    "error_message": result.error_message,
                    "warnings": result.warnings,
                    "processed_at": result.repo_metadata.processed_at.isoformat(),
                    "languages": result.repo_metadata.languages,
                    "total_files": result.repo_metadata.total_files,
                    "processed_files": result.repo_metadata.processed_files
                }
                results_data.append(result_dict)
            
            with open(output_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results to {output_file}: {str(e)}")
    
    def print_pipeline_status(self) -> None:
        """Print current pipeline status."""
        if not self.pipeline:
            print("❌ Pipeline not initialized")
            return
        
        status = self.pipeline.get_pipeline_status()
        
        print("\n🔧 Pipeline Status:")
        print(f"   Vector Service: {'✅ Ready' if status['vector_service']['ready'] else '❌ Not Ready'}")
        if status['vector_service']['ready']:
            print(f"      • Project: {status['vector_service']['project_id']}")
            print(f"      • Location: {status['vector_service']['location']}")
        
        print(f"   Pipeline Stages:")
        for stage_name, stage_info in status['stages'].items():
            print(f"      • {stage_name.title()}: {'✅' if stage_info['ready'] else '❌'}")
        
        print(f"   Configuration:")
        print(f"      • Max chunk size: {status['configuration']['max_chunk_size']}")
        print(f"      • Overlap size: {status['configuration']['overlap_size']}")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Ingest GitHub repositories into vector search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo
  %(prog)s --batch repos.txt --output results.json
  %(prog)s https://github.com/owner/repo --chunk-size 1500 --verbose
        """
    )
    
    # Main arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "repo_url",
        nargs="?",
        help="GitHub repository URL to ingest"
    )
    group.add_argument(
        "--batch",
        metavar="FILE",
        help="File containing list of repository URLs (one per line)"
    )
    group.add_argument(
        "--status",
        action="store_true",
        help="Show pipeline status and exit"
    )
    
    # Configuration options
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Maximum size of code chunks (default: 1000)"
    )
    parser.add_argument(
        "--overlap-size",
        type=int,
        default=100,
        help="Overlap size between chunks (default: 100)"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information"
    )
    
    return parser


async def main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create CLI instance
    cli = IngestionCLI()
    cli.verbose = args.verbose
    
    # Initialize services
    print("🔧 Initializing services...")
    if not await cli.initialize_services():
        print("❌ Failed to initialize services. Check your configuration.")
        sys.exit(1)
    
    # Handle status command
    if args.status:
        cli.print_pipeline_status()
        return
    
    # Update pipeline configuration if specified
    if hasattr(args, 'chunk_size') and args.chunk_size != 1000:
        cli.pipeline.chunk_stage.max_chunk_size = args.chunk_size
    if hasattr(args, 'overlap_size') and args.overlap_size != 100:
        cli.pipeline.chunk_stage.overlap_size = args.overlap_size
    
    results = []
    
    try:
        if args.batch:
            # Batch processing
            urls = cli.load_urls_from_file(args.batch)
            if not urls:
                print(f"❌ No valid URLs found in {args.batch}")
                sys.exit(1)
            
            results = await cli.ingest_multiple_repositories(urls)
            
        elif args.repo_url:
            # Single repository processing
            result = await cli.ingest_single_repository(args.repo_url)
            results = [result]
        
        # Save results if output file specified
        if args.output and results:
            cli.save_results_to_file(results, args.output)
        
        # Exit with appropriate code
        failed_count = len([r for r in results if not r.success])
        if failed_count > 0:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the CLI
    asyncio.run(main())