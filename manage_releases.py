#!/usr/bin/env python3
"""
Release Tracker Management Script

This script manages releases in the Notion Release Tracker database.

Usage:
    python manage_releases.py add                    # Add a new release (interactive)
    python manage_releases.py add --version v1.1.0   # Add with version
    python manage_releases.py list                   # List all releases
    python manage_releases.py latest                 # Show latest release
    python manage_releases.py view v1.0.0            # View specific release
"""

import os
import argparse
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv


class ReleaseManager:
    """Manages releases in Notion Release Tracker."""
    
    def __init__(self):
        """Initialize Notion client."""
        load_dotenv()
        
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("RELEASE_DATABASE_ID")
        
        if not self.database_id:
            print("❌ RELEASE_DATABASE_ID not found in .env file")
            print("   Please run create_release_tracker.py first")
            exit(1)
    
    def add_release(self, version=None, release_type=None, status=None, 
                   description=None, changes=None, components=None):
        """
        Add a new release to the tracker.
        
        Args:
            version: Version number (e.g., v1.1.0)
            release_type: Major, Minor, Patch, Hotfix
            status: Planning, In Progress, Testing, Deployed, Rolled Back
            description: Brief description
            changes: Detailed changelog
            components: List of affected components
        """
        print("=" * 60)
        print("➕ Adding New Release")
        print("=" * 60)
        
        # Interactive mode if values not provided
        if not version:
            version = input("\nVersion (e.g., v1.1.0): ").strip()
        
        if not release_type:
            print("\nRelease Type:")
            print("  1. Major")
            print("  2. Minor")
            print("  3. Patch")
            print("  4. Hotfix")
            type_choice = input("Choose (1-4): ").strip()
            release_type = ["Major", "Minor", "Patch", "Hotfix"][int(type_choice) - 1]
        
        if not status:
            print("\nStatus:")
            print("  1. Planning")
            print("  2. In Progress")
            print("  3. Testing")
            print("  4. Deployed")
            print("  5. Rolled Back")
            status_choice = input("Choose (1-5): ").strip()
            status = ["Planning", "In Progress", "Testing", "Deployed", "Rolled Back"][int(status_choice) - 1]
        
        if not description:
            description = input("\nDescription: ").strip()
        
        if not changes:
            print("\nChanges (enter multiple lines, empty line to finish):")
            change_lines = []
            while True:
                line = input("  - ")
                if not line:
                    break
                change_lines.append(f"- {line}")
            changes = "\n".join(change_lines)
        
        if not components:
            print("\nComponents (comma-separated):")
            print("  Options: Database, Sync Script, Notifications, Scheduler, API Integration, Documentation")
            comp_input = input("Components: ").strip()
            components = [c.strip() for c in comp_input.split(",") if c.strip()]
        
        breaking = input("\nBreaking changes? (y/n): ").strip().lower() == 'y'
        deployed_by = input("Deployed by: ").strip() or "Eric Schneider"
        
        # Create the release
        try:
            properties = {
                "Version": {"title": [{"text": {"content": version}}]},
                "Release Date": {"date": {"start": datetime.now().isoformat()}},
                "Type": {"select": {"name": release_type}},
                "Status": {"select": {"name": status}},
                "Description": {"rich_text": [{"text": {"content": description}}]},
                "Breaking Changes": {"checkbox": breaking},
                "Deployed By": {"rich_text": [{"text": {"content": deployed_by}}]}
            }
            
            if changes:
                properties["Changes"] = {"rich_text": [{"text": {"content": changes}}]}
            
            if components:
                properties["Component"] = {
                    "multi_select": [{"name": comp} for comp in components]
                }
            
            self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            print(f"\n✅ Release {version} added successfully!")
            
        except Exception as e:
            print(f"\n❌ Error adding release: {e}")
    
    def list_releases(self):
        """List all releases."""
        print("=" * 60)
        print("📋 All Releases")
        print("=" * 60)
        
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                sorts=[
                    {
                        "property": "Release Date",
                        "direction": "descending"
                    }
                ]
            )
            
            if not results["results"]:
                print("\n   No releases found")
                return
            
            print(f"\n   Found {len(results['results'])} release(s):\n")
            
            for page in results["results"]:
                props = page["properties"]
                
                version = props["Version"]["title"][0]["text"]["content"] if props["Version"]["title"] else "N/A"
                date = props["Release Date"]["date"]["start"] if props["Release Date"]["date"] else "N/A"
                release_type = props["Type"]["select"]["name"] if props["Type"]["select"] else "N/A"
                status = props["Status"]["select"]["name"] if props["Status"]["select"] else "N/A"
                description = props["Description"]["rich_text"][0]["text"]["content"] if props["Description"]["rich_text"] else ""
                
                # Format date
                try:
                    dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = date
                
                # Status emoji
                status_emoji = {
                    "Planning": "📝",
                    "In Progress": "🔨",
                    "Testing": "🧪",
                    "Deployed": "✅",
                    "Rolled Back": "⚠️"
                }.get(status, "📦")
                
                print(f"   {status_emoji} {version} ({release_type}) - {date_str}")
                print(f"      Status: {status}")
                if description:
                    print(f"      {description[:60]}{'...' if len(description) > 60 else ''}")
                print()
            
        except Exception as e:
            print(f"\n❌ Error listing releases: {e}")
    
    def get_latest_release(self):
        """Get the latest release."""
        print("=" * 60)
        print("🏷️  Latest Release")
        print("=" * 60)
        
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                sorts=[
                    {
                        "property": "Release Date",
                        "direction": "descending"
                    }
                ],
                page_size=1
            )
            
            if not results["results"]:
                print("\n   No releases found")
                return
            
            page = results["results"][0]
            self._display_release_details(page)
            
        except Exception as e:
            print(f"\n❌ Error getting latest release: {e}")
    
    def view_release(self, version):
        """View details of a specific release."""
        print("=" * 60)
        print(f"🔍 Release: {version}")
        print("=" * 60)
        
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Version",
                    "title": {
                        "equals": version
                    }
                }
            )
            
            if not results["results"]:
                print(f"\n   Release {version} not found")
                return
            
            page = results["results"][0]
            self._display_release_details(page)
            
        except Exception as e:
            print(f"\n❌ Error viewing release: {e}")
    
    def _display_release_details(self, page):
        """Display detailed information about a release."""
        props = page["properties"]
        
        version = props["Version"]["title"][0]["text"]["content"] if props["Version"]["title"] else "N/A"
        date = props["Release Date"]["date"]["start"] if props["Release Date"]["date"] else "N/A"
        release_type = props["Type"]["select"]["name"] if props["Type"]["select"] else "N/A"
        status = props["Status"]["select"]["name"] if props["Status"]["select"] else "N/A"
        description = props["Description"]["rich_text"][0]["text"]["content"] if props["Description"]["rich_text"] else ""
        changes = props["Changes"]["rich_text"][0]["text"]["content"] if props["Changes"]["rich_text"] else ""
        breaking = props["Breaking Changes"]["checkbox"]
        deployed_by = props["Deployed By"]["rich_text"][0]["text"]["content"] if props["Deployed By"]["rich_text"] else ""
        components = [c["name"] for c in props["Component"]["multi_select"]] if props["Component"]["multi_select"] else []
        
        # Format date
        try:
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d %I:%M %p")
        except:
            date_str = date
        
        print(f"\n   Version: {version}")
        print(f"   Type: {release_type}")
        print(f"   Status: {status}")
        print(f"   Release Date: {date_str}")
        
        if deployed_by:
            print(f"   Deployed By: {deployed_by}")
        
        if components:
            print(f"   Components: {', '.join(components)}")
        
        if breaking:
            print("   ⚠️  Breaking Changes: YES")
        
        if description:
            print(f"\n   Description:")
            print(f"   {description}")
        
        if changes:
            print(f"\n   Changes:")
            for line in changes.split('\n'):
                print(f"   {line}")
        
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manage releases in Notion Release Tracker"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new release")
    add_parser.add_argument("--version", help="Version number (e.g., v1.1.0)")
    add_parser.add_argument("--type", choices=["Major", "Minor", "Patch", "Hotfix"], help="Release type")
    add_parser.add_argument("--status", choices=["Planning", "In Progress", "Testing", "Deployed", "Rolled Back"], help="Release status")
    add_parser.add_argument("--description", help="Brief description")
    
    # List command
    subparsers.add_parser("list", help="List all releases")
    
    # Latest command
    subparsers.add_parser("latest", help="Show latest release")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View specific release")
    view_parser.add_argument("version", help="Version to view (e.g., v1.0.0)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load environment
    load_dotenv()
    if not os.getenv("RELEASE_DATABASE_ID"):
        print("❌ RELEASE_DATABASE_ID not found in .env file")
        print("   Please run create_release_tracker.py first")
        return
    
    try:
        manager = ReleaseManager()
        
        if args.command == "add":
            manager.add_release(
                version=args.version,
                release_type=args.type,
                status=args.status,
                description=args.description
            )
        elif args.command == "list":
            manager.list_releases()
        elif args.command == "latest":
            manager.get_latest_release()
        elif args.command == "view":
            manager.view_release(args.version)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
