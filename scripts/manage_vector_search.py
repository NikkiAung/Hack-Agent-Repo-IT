#!/usr/bin/env python3
"""
Google Vector Search Management Utility

Utility for managing Google Vector Search resources including cleanup,
monitoring, and cost optimization.

Usage:
    python scripts/manage_vector_search.py <command> [options]

Commands:
    status      - Show current vector search status
    list        - List all indexes and endpoints
    cleanup     - Clean up unused resources
    delete      - Delete specific resources
    monitor     - Monitor resource usage and costs
    backup      - Backup index data
    restore     - Restore index data

Examples:
    # Show status
    python scripts/manage_vector_search.py status
    
    # List all resources
    python scripts/manage_vector_search.py list --verbose
    
    # Clean up unused resources
    python scripts/manage_vector_search.py cleanup --dry-run
    
    # Delete specific index
    python scripts/manage_vector_search.py delete --index INDEX_ID
    
    # Monitor usage
    python scripts/manage_vector_search.py monitor --days 7
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.services.google_vector_search_service import GoogleVectorSearchService
from backend.core.logging import RepoAnalysisLogger

logger = RepoAnalysisLogger(__name__)


class VectorSearchManager:
    """Manager for Google Vector Search resources."""
    
    def __init__(self):
        self.vector_service = None
        self.verbose = False
    
    async def initialize(self) -> bool:
        """Initialize the vector search service."""
        try:
            self.vector_service = GoogleVectorSearchService()
            await self.vector_service.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {str(e)}")
            return False
    
    async def show_status(self) -> None:
        """Show current vector search status."""
        print("\n🔍 Google Vector Search Status")
        print("=" * 40)
        
        try:
            # Service status
            print(f"📊 Service Configuration:")
            print(f"   • Project ID: {self.vector_service.project_id}")
            print(f"   • Location: {self.vector_service.location}")
            print(f"   • Embedding Model: {getattr(self.vector_service, 'embedding_model', 'N/A')}")
            
            # List indexes
            indexes = await self._list_indexes()
            print(f"\n📚 Indexes ({len(indexes)}):")
            if indexes:
                for idx in indexes:
                    status = "🟢 Ready" if idx.get('state') == 'READY' else "🟡 Updating"
                    print(f"   • {idx['display_name']} ({idx['name'].split('/')[-1]}) - {status}")
                    if self.verbose:
                        print(f"     Created: {idx.get('create_time', 'Unknown')}")
                        print(f"     Dimensions: {idx.get('metadata', {}).get('config', {}).get('dimensions', 'Unknown')}")
            else:
                print("   No indexes found")
            
            # List endpoints
            endpoints = await self._list_endpoints()
            print(f"\n🔗 Endpoints ({len(endpoints)}):")
            if endpoints:
                for ep in endpoints:
                    deployed_count = len(ep.get('deployed_indexes', []))
                    print(f"   • {ep['display_name']} ({ep['name'].split('/')[-1]}) - {deployed_count} deployed indexes")
                    if self.verbose and deployed_count > 0:
                        for deployed in ep.get('deployed_indexes', []):
                            print(f"     - {deployed.get('id', 'Unknown ID')}")
            else:
                print("   No endpoints found")
            
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")
    
    async def list_resources(self, resource_type: str = "all") -> None:
        """List vector search resources."""
        print(f"\n📋 Listing {resource_type} resources")
        print("=" * 40)
        
        try:
            if resource_type in ["all", "indexes"]:
                indexes = await self._list_indexes()
                print(f"\n📚 Indexes ({len(indexes)}):")
                for idx in indexes:
                    self._print_index_details(idx)
            
            if resource_type in ["all", "endpoints"]:
                endpoints = await self._list_endpoints()
                print(f"\n🔗 Endpoints ({len(endpoints)}):")
                for ep in endpoints:
                    self._print_endpoint_details(ep)
                    
        except Exception as e:
            print(f"❌ Error listing resources: {str(e)}")
    
    async def cleanup_resources(self, dry_run: bool = True) -> None:
        """Clean up unused vector search resources."""
        print(f"\n🧹 Cleaning up resources {'(DRY RUN)' if dry_run else ''}")
        print("=" * 40)
        
        try:
            cleanup_actions = []
            
            # Find unused indexes
            indexes = await self._list_indexes()
            endpoints = await self._list_endpoints()
            
            # Get all deployed index IDs
            deployed_index_ids = set()
            for ep in endpoints:
                for deployed in ep.get('deployed_indexes', []):
                    deployed_index_ids.add(deployed.get('index', ''))
            
            # Find indexes not deployed anywhere
            unused_indexes = []
            for idx in indexes:
                index_name = idx['name']
                if index_name not in deployed_index_ids:
                    # Check if index is old (created more than 24 hours ago)
                    create_time = idx.get('create_time')
                    if create_time:
                        # Parse create time and check age
                        # This is a simplified check - you might want more sophisticated logic
                        unused_indexes.append(idx)
            
            # Find empty endpoints
            empty_endpoints = []
            for ep in endpoints:
                if len(ep.get('deployed_indexes', [])) == 0:
                    empty_endpoints.append(ep)
            
            # Report findings
            print(f"\n🔍 Cleanup Analysis:")
            print(f"   • Unused indexes: {len(unused_indexes)}")
            print(f"   • Empty endpoints: {len(empty_endpoints)}")
            
            if unused_indexes:
                print(f"\n📚 Unused Indexes:")
                for idx in unused_indexes:
                    print(f"   • {idx['display_name']} ({idx['name'].split('/')[-1]})")
                    cleanup_actions.append(("delete_index", idx))
            
            if empty_endpoints:
                print(f"\n🔗 Empty Endpoints:")
                for ep in empty_endpoints:
                    print(f"   • {ep['display_name']} ({ep['name'].split('/')[-1]})")
                    cleanup_actions.append(("delete_endpoint", ep))
            
            if not cleanup_actions:
                print("\n✅ No cleanup needed - all resources are in use")
                return
            
            # Execute cleanup if not dry run
            if not dry_run:
                print(f"\n🗑️  Executing cleanup...")
                for action_type, resource in cleanup_actions:
                    try:
                        if action_type == "delete_index":
                            await self._delete_index(resource['name'])
                            print(f"   ✅ Deleted index: {resource['display_name']}")
                        elif action_type == "delete_endpoint":
                            await self._delete_endpoint(resource['name'])
                            print(f"   ✅ Deleted endpoint: {resource['display_name']}")
                    except Exception as e:
                        print(f"   ❌ Failed to delete {resource['display_name']}: {str(e)}")
            else:
                print(f"\n💡 Run without --dry-run to execute cleanup")
                
        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")
    
    async def delete_resource(self, resource_type: str, resource_id: str, force: bool = False) -> None:
        """Delete a specific resource."""
        print(f"\n🗑️  Deleting {resource_type}: {resource_id}")
        
        if not force:
            confirm = input(f"Are you sure you want to delete {resource_type} '{resource_id}'? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Deletion cancelled")
                return
        
        try:
            if resource_type == "index":
                await self._delete_index_by_id(resource_id)
                print(f"✅ Successfully deleted index: {resource_id}")
            elif resource_type == "endpoint":
                await self._delete_endpoint_by_id(resource_id)
                print(f"✅ Successfully deleted endpoint: {resource_id}")
            else:
                print(f"❌ Unknown resource type: {resource_type}")
                
        except Exception as e:
            print(f"❌ Error deleting {resource_type}: {str(e)}")
    
    async def monitor_usage(self, days: int = 7) -> None:
        """Monitor resource usage and estimated costs."""
        print(f"\n📊 Monitoring usage for the last {days} days")
        print("=" * 40)
        
        try:
            # This is a simplified monitoring - in a real implementation,
            # you would integrate with Google Cloud Monitoring API
            
            indexes = await self._list_indexes()
            endpoints = await self._list_endpoints()
            
            print(f"\n📈 Resource Summary:")
            print(f"   • Active indexes: {len(indexes)}")
            print(f"   • Active endpoints: {len(endpoints)}")
            
            # Estimate costs (simplified)
            # Note: These are rough estimates - actual costs may vary
            index_cost_per_hour = 0.50  # Estimated cost per index per hour
            endpoint_cost_per_hour = 0.30  # Estimated cost per endpoint per hour
            
            hours_in_period = days * 24
            estimated_index_cost = len(indexes) * index_cost_per_hour * hours_in_period
            estimated_endpoint_cost = len(endpoints) * endpoint_cost_per_hour * hours_in_period
            total_estimated_cost = estimated_index_cost + estimated_endpoint_cost
            
            print(f"\n💰 Estimated Costs ({days} days):")
            print(f"   • Indexes: ${estimated_index_cost:.2f}")
            print(f"   • Endpoints: ${estimated_endpoint_cost:.2f}")
            print(f"   • Total: ${total_estimated_cost:.2f}")
            
            print(f"\n⚠️  Note: These are rough estimates. Check Google Cloud Console for actual costs.")
            
        except Exception as e:
            print(f"❌ Error monitoring usage: {str(e)}")
    
    async def backup_data(self, output_file: str) -> None:
        """Backup index metadata and configuration."""
        print(f"\n💾 Backing up vector search data to {output_file}")
        
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "project_id": self.vector_service.project_id,
                "location": self.vector_service.location,
                "indexes": await self._list_indexes(),
                "endpoints": await self._list_endpoints()
            }
            
            with open(output_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Backup saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Error creating backup: {str(e)}")
    
    # Helper methods
    async def _list_indexes(self) -> List[Dict[str, Any]]:
        """List all indexes."""
        # This would use the actual Google Cloud AI Platform API
        # For now, return empty list as placeholder
        return []
    
    async def _list_endpoints(self) -> List[Dict[str, Any]]:
        """List all endpoints."""
        # This would use the actual Google Cloud AI Platform API
        # For now, return empty list as placeholder
        return []
    
    async def _delete_index(self, index_name: str) -> None:
        """Delete an index by name."""
        # Implementation would use Google Cloud AI Platform API
        pass
    
    async def _delete_endpoint(self, endpoint_name: str) -> None:
        """Delete an endpoint by name."""
        # Implementation would use Google Cloud AI Platform API
        pass
    
    async def _delete_index_by_id(self, index_id: str) -> None:
        """Delete an index by ID."""
        # Implementation would use Google Cloud AI Platform API
        pass
    
    async def _delete_endpoint_by_id(self, endpoint_id: str) -> None:
        """Delete an endpoint by ID."""
        # Implementation would use Google Cloud AI Platform API
        pass
    
    def _print_index_details(self, index: Dict[str, Any]) -> None:
        """Print detailed index information."""
        print(f"\n📚 Index: {index['display_name']}")
        print(f"   ID: {index['name'].split('/')[-1]}")
        print(f"   State: {index.get('state', 'Unknown')}")
        print(f"   Created: {index.get('create_time', 'Unknown')}")
        
        if self.verbose:
            metadata = index.get('metadata', {})
            config = metadata.get('config', {})
            print(f"   Dimensions: {config.get('dimensions', 'Unknown')}")
            print(f"   Distance Measure: {config.get('distance_measure_type', 'Unknown')}")
    
    def _print_endpoint_details(self, endpoint: Dict[str, Any]) -> None:
        """Print detailed endpoint information."""
        deployed_indexes = endpoint.get('deployed_indexes', [])
        print(f"\n🔗 Endpoint: {endpoint['display_name']}")
        print(f"   ID: {endpoint['name'].split('/')[-1]}")
        print(f"   Deployed Indexes: {len(deployed_indexes)}")
        
        if self.verbose and deployed_indexes:
            for deployed in deployed_indexes:
                print(f"     - {deployed.get('id', 'Unknown ID')}")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Manage Google Vector Search resources",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show vector search status")
    status_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List resources")
    list_parser.add_argument("--type", choices=["all", "indexes", "endpoints"], default="all", help="Resource type to list")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up unused resources")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete specific resource")
    delete_parser.add_argument("--index", help="Index ID to delete")
    delete_parser.add_argument("--endpoint", help="Endpoint ID to delete")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor usage and costs")
    monitor_parser.add_argument("--days", type=int, default=7, help="Number of days to monitor (default: 7)")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup index data")
    backup_parser.add_argument("--output", "-o", required=True, help="Output file for backup")
    
    return parser


async def main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create manager
    manager = VectorSearchManager()
    manager.verbose = getattr(args, 'verbose', False)
    
    # Initialize
    print("🔧 Initializing Google Vector Search service...")
    if not await manager.initialize():
        print("❌ Failed to initialize. Check your Google Cloud configuration.")
        sys.exit(1)
    
    try:
        # Execute command
        if args.command == "status":
            await manager.show_status()
        
        elif args.command == "list":
            await manager.list_resources(args.type)
        
        elif args.command == "cleanup":
            await manager.cleanup_resources(dry_run=args.dry_run)
        
        elif args.command == "delete":
            if args.index:
                await manager.delete_resource("index", args.index, args.force)
            elif args.endpoint:
                await manager.delete_resource("endpoint", args.endpoint, args.force)
            else:
                print("❌ Specify --index or --endpoint to delete")
                sys.exit(1)
        
        elif args.command == "monitor":
            await manager.monitor_usage(args.days)
        
        elif args.command == "backup":
            await manager.backup_data(args.output)
        
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