#!/usr/bin/env python3
"""
Add League Property to Existing Notion Database

This script adds the "League" property to your existing Soccer Schedule Tracker database
without losing any data.

Usage:
    python add_league_property.py
"""

import os
from notion_client import Client
from dotenv import load_dotenv


def add_league_property(notion_token, database_id):
    """
    Add League property to existing database.
    
    Args:
        notion_token: Notion API token
        database_id: Database ID to update
    """
    notion = Client(auth=notion_token)
    
    print("=" * 60)
    print("📊 Add League Property to Database")
    print("=" * 60)
    print(f"\nDatabase ID: {database_id}")
    
    # Check current database structure
    print("\n1️⃣ Checking current database structure...")
    try:
        database = notion.databases.retrieve(database_id=database_id)
        properties = database['properties']
        
        # Check if League already exists
        if 'League' in properties:
            print("   ⚠️  League property already exists!")
            print("   No changes needed.")
            return
        
        print("   ✅ Database found")
        print(f"   Current properties: {', '.join(properties.keys())}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Add League property
    print("\n2️⃣ Adding League property...")
    try:
        # Update database schema to add League property
        notion.databases.update(
            database_id=database_id,
            properties={
                "League": {
                    "select": {
                        "options": [
                            {"name": "Premier League", "color": "purple"},
                            {"name": "Bundesliga", "color": "red"},
                            {"name": "MLS", "color": "blue"},
                            {"name": "La Liga", "color": "orange"},
                            {"name": "Serie A", "color": "green"},
                            {"name": "Ligue 1", "color": "pink"}
                        ]
                    }
                }
            }
        )
        print("   ✅ League property added successfully!")
    
    except Exception as e:
        print(f"   ❌ Error adding property: {e}")
        return
    
    # Update Team property options
    print("\n3️⃣ Updating Team property options...")
    try:
        notion.databases.update(
            database_id=database_id,
            properties={
                "Team": {
                    "select": {
                        "options": [
                            {"name": "Manchester United", "color": "red"},
                            {"name": "Manchester City", "color": "blue"},
                            {"name": "Borussia Dortmund", "color": "yellow"},
                            {"name": "Brentford FC", "color": "red"},
                            {"name": "Columbus Crew", "color": "yellow"}
                        ]
                    }
                }
            }
        )
        print("   ✅ Team options updated!")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not update Team options: {e}")
    
    # Update Competition property options
    print("\n4️⃣ Updating Competition property options...")
    try:
        notion.databases.update(
            database_id=database_id,
            properties={
                "Competition": {
                    "select": {
                        "options": [
                            {"name": "Premier League", "color": "purple"},
                            {"name": "Bundesliga", "color": "red"},
                            {"name": "FA Cup", "color": "blue"},
                            {"name": "League Cup", "color": "orange"},
                            {"name": "DFB Pokal", "color": "red"},
                            {"name": "Champions League", "color": "default"},
                            {"name": "Europa League", "color": "green"},
                            {"name": "MLS Regular Season", "color": "pink"},
                            {"name": "MLS Playoffs", "color": "brown"},
                            {"name": "US Open Cup", "color": "gray"},
                            {"name": "Leagues Cup", "color": "yellow"}
                        ]
                    }
                }
            }
        )
        print("   ✅ Competition options updated!")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not update Competition options: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Database Updated Successfully!")
    print("=" * 60)
    print("\nThe League property has been added to your database.")
    print("You can now run sync_matches_footballdata.py to populate it!")


def main():
    """Main function."""
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_token or not database_id:
        print("❌ Missing required environment variables:")
        if not notion_token:
            print("   - NOTION_TOKEN")
        if not database_id:
            print("   - NOTION_DATABASE_ID")
        print("\nPlease check your .env file.")
        return
    
    add_league_property(notion_token, database_id)


if __name__ == "__main__":
    main()
