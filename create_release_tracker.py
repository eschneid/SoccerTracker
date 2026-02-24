#!/usr/bin/env python3
"""
Create Release Tracker Database in Notion

This script creates a Release Tracker database to track software releases,
deployments, and version history for your soccer tracker project.

Usage:
    python create_release_tracker.py
"""

import os
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime


class ReleaseTrackerCreator:
    """Creates a Release Tracker database in Notion."""
    
    def __init__(self):
        """Initialize Notion client."""
        load_dotenv()
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        # Use the Soccer Tracker page ID
        self.parent_page_id = "30741253de0180ecb239f86cfcd83e64"
        self.database_id = None
    
    def create_database(self):
        """Create the Release Tracker database."""
        print("=" * 60)
        print("📦 Creating Release Tracker Database")
        print("=" * 60)
        print(f"\nParent Page ID: {self.parent_page_id}")
        
        database_properties = {
            "Version": {
                "title": {}
            },
            "Release Date": {
                "date": {}
            },
            "Type": {
                "select": {
                    "options": [
                        {"name": "Major", "color": "red"},
                        {"name": "Minor", "color": "blue"},
                        {"name": "Patch", "color": "green"},
                        {"name": "Hotfix", "color": "orange"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Planning", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Testing", "color": "orange"},
                        {"name": "Deployed", "color": "green"},
                        {"name": "Rolled Back", "color": "red"}
                    ]
                }
            },
            "Component": {
                "multi_select": {
                    "options": [
                        {"name": "Database", "color": "purple"},
                        {"name": "Sync Script", "color": "blue"},
                        {"name": "Notifications", "color": "pink"},
                        {"name": "Scheduler", "color": "orange"},
                        {"name": "API Integration", "color": "green"},
                        {"name": "Documentation", "color": "gray"}
                    ]
                }
            },
            "Description": {
                "rich_text": {}
            },
            "Changes": {
                "rich_text": {}
            },
            "Breaking Changes": {
                "checkbox": {}
            },
            "Deployed By": {
                "rich_text": {}
            },
            "Git Commit": {
                "url": {}
            },
            "Issues Fixed": {
                "rich_text": {}
            },
            "Notes": {
                "rich_text": {}
            }
        }
        
        try:
            response = self.notion.databases.create(
                parent={"page_id": self.parent_page_id},
                title=[
                    {
                        "type": "text",
                        "text": {
                            "content": "📦 Release Tracker"
                        }
                    }
                ],
                properties=database_properties,
                icon={
                    "type": "emoji",
                    "emoji": "📦"
                }
            )
            
            self.database_id = response["id"]
            print("\n✅ Database created successfully!")
            print(f"Database ID: {self.database_id}")
            print(f"URL: https://notion.so/{self.database_id.replace('-', '')}")
            
            return response
            
        except Exception as e:
            print(f"\n❌ Error creating database: {e}")
            raise
    
    def add_initial_release(self):
        """Add the initial v1.0 release entry."""
        if not self.database_id:
            print("❌ Database ID not set. Create database first.")
            return
        
        print("\n📝 Adding initial release entry...")
        
        try:
            self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Version": {"title": [{"text": {"content": "v1.0.0"}}]},
                    "Release Date": {"date": {"start": datetime.now().isoformat()}},
                    "Type": {"select": {"name": "Major"}},
                    "Status": {"select": {"name": "Deployed"}},
                    "Component": {
                        "multi_select": [
                            {"name": "Database"},
                            {"name": "Sync Script"},
                            {"name": "Notifications"},
                            {"name": "API Integration"}
                        ]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": "Initial release of Soccer Tracker system"}}]
                    },
                    "Changes": {
                        "rich_text": [{"text": {"content": 
                            "- Notion database for match tracking\n"
                            "- Football-Data.org API integration\n"
                            "- SMS notifications via email-to-SMS gateway\n"
                            "- Support for Premier League and Bundesliga\n"
                            "- Game day notifications\n"
                            "- Teams: Man United, Man City, Dortmund, Brentford"
                        }}]
                    },
                    "Breaking Changes": {"checkbox": False},
                    "Deployed By": {"rich_text": [{"text": {"content": "Eric Schneider"}}]}
                }
            )
            print("   ✅ Added v1.0.0 release entry")
            
        except Exception as e:
            print(f"   ❌ Error adding release: {e}")
    
    def save_database_id(self):
        """Save the database ID to .env file."""
        if not self.database_id:
            return
        
        try:
            # Read existing .env
            env_path = ".env"
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            # Check if RELEASE_DATABASE_ID already exists
            found = False
            for i, line in enumerate(lines):
                if line.startswith("RELEASE_DATABASE_ID="):
                    lines[i] = f"RELEASE_DATABASE_ID={self.database_id}\n"
                    found = True
                    break
            
            # If not found, add it
            if not found:
                lines.append(f"\n# Release Tracker Database\n")
                lines.append(f"RELEASE_DATABASE_ID={self.database_id}\n")
            
            # Write back
            with open(env_path, "w") as f:
                f.writelines(lines)
            
            print("\n✅ Database ID saved to .env file")
            
        except Exception as e:
            print(f"\n⚠️  Could not save to .env: {e}")


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("📦 Release Tracker Database Setup")
    print("=" * 60)
    
    try:
        creator = ReleaseTrackerCreator()
        
        # Create database
        creator.create_database()
        
        # Add initial release
        add_initial = input("\nAdd initial v1.0.0 release entry? (y/n): ").strip().lower()
        if add_initial == 'y':
            creator.add_initial_release()
        
        # Save to .env
        creator.save_database_id()
        
        print("\n" + "=" * 60)
        print("✅ Release Tracker Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. View your Release Tracker in Notion")
        print("2. Use manage_releases.py to add/view releases")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
