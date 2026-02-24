#!/usr/bin/env python3
"""
Notion Database Truncate Utility

This script clears all entries from your Soccer Schedule Tracker database.
Use with caution - this cannot be undone!

Usage:
    python truncate_notion_db.py
    python truncate_notion_db.py --yes  (skip confirmation)
"""

import os
import sys
from notion_client import Client
from dotenv import load_dotenv


def truncate_database(notion_token, database_id, skip_confirm=False):
    """
    Delete all pages from the Notion database.
    
    Args:
        notion_token: Notion API token
        database_id: Database ID to truncate
        skip_confirm: If True, skip confirmation prompt
    """
    notion = Client(auth=notion_token)
    
    print("=" * 60)
    print("🗑️  Notion Database Truncate Utility")
    print("=" * 60)
    print(f"\nDatabase ID: {database_id}")
    
    # Query all pages
    print("\n📊 Counting entries...")
    try:
        has_more = True
        all_pages = []
        start_cursor = None
        
        while has_more:
            if start_cursor:
                results = notion.databases.query(
                    database_id=database_id,
                    start_cursor=start_cursor
                )
            else:
                results = notion.databases.query(database_id=database_id)
            
            all_pages.extend(results['results'])
            has_more = results['has_more']
            start_cursor = results.get('next_cursor')
        
        total_entries = len(all_pages)
        print(f"   Found {total_entries} entries")
        
        if total_entries == 0:
            print("\n✅ Database is already empty!")
            return
        
    except Exception as e:
        print(f"\n❌ Error querying database: {e}")
        return
    
    # Confirmation
    if not skip_confirm:
        print("\n⚠️  WARNING: This will DELETE ALL ENTRIES from the database!")
        print("   This action CANNOT be undone.")
        print(f"   {total_entries} entries will be deleted.")
        
        confirm = input("\n   Type 'DELETE' to confirm: ").strip()
        
        if confirm != 'DELETE':
            print("\n❌ Truncate cancelled.")
            return
    
    # Delete all pages
    print(f"\n🗑️  Deleting {total_entries} entries...")
    deleted = 0
    failed = 0
    
    for i, page in enumerate(all_pages, 1):
        try:
            notion.pages.update(
                page_id=page['id'],
                archived=True
            )
            deleted += 1
            
            # Progress indicator every 10 entries
            if i % 10 == 0:
                print(f"   Progress: {i}/{total_entries} ({(i/total_entries)*100:.1f}%)")
        
        except Exception as e:
            print(f"   ⚠️  Failed to delete entry {i}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("✅ Truncate Complete!")
    print("=" * 60)
    print(f"   Deleted: {deleted} entries")
    if failed > 0:
        print(f"   Failed: {failed} entries")


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
    
    # Check for --yes flag
    skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
    
    truncate_database(notion_token, database_id, skip_confirm)


if __name__ == "__main__":
    main()
