#!/usr/bin/env python3
"""
Game Day SMS Notifications

This script checks for matches happening today and sends SMS notifications
via email-to-SMS gateway.

Usage:
    python notify_gameday.py              # Check and send notifications
    python notify_gameday.py --test       # Send test message
    python notify_gameday.py --preview    # Show what would be sent (no SMS)
"""

import os
import argparse
from datetime import datetime, timedelta
from notion_client import Client
from dotenv import load_dotenv
from send_text import send_text
import pytz


class GameDayNotifier:
    """Manages game day SMS notifications."""
    
    def __init__(self):
        """Initialize Notion client."""
        load_dotenv()
        
        # Notion setup
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        # Favorite teams (for personalized messages)
        self.my_team = os.getenv("MY_FAVORITE_TEAM", "Manchester United")
        self.wife_team = os.getenv("WIFE_FAVORITE_TEAM", "Brentford FC")
    
    def get_today_matches(self):
        """
        Get matches happening today from Notion (in EST timezone).
        
        Returns:
            list: List of today's matches
        """
        # Get today's date range in EST
        est = pytz.timezone('America/New_York')
        now_est = datetime.now(est)
        today_start = now_est.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Convert to UTC for Notion query
        today_start_utc = today_start.astimezone(pytz.UTC)
        today_end_utc = today_end.astimezone(pytz.UTC)
        
        today_start_str = today_start_utc.isoformat()
        today_end_str = today_end_utc.isoformat()
        
        print(f"\n🔍 Checking for matches today ({today_start.strftime('%Y-%m-%d')} EST)...")
        
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "Match Date",
                            "date": {
                                "on_or_after": today_start_str
                            }
                        },
                        {
                            "property": "Match Date",
                            "date": {
                                "before": today_end_str
                            }
                        },
                        {
                            "or": [
                                {
                                    "property": "Status",
                                    "select": {
                                        "equals": "Scheduled"
                                    }
                                },
                                {
                                    "property": "Status",
                                    "select": {
                                        "equals": "Live"
                                    }
                                }
                            ]
                        }
                    ]
                },
                sorts=[
                    {
                        "property": "Match Date",
                        "direction": "ascending"
                    }
                ]
            )
            
            matches = []
            for page in results["results"]:
                props = page["properties"]
                
                match = {
                    "team": props["Team"]["select"]["name"] if props["Team"]["select"] else "",
                    "opponent": props["Opponent"]["title"][0]["text"]["content"] if props["Opponent"]["title"] else "",
                    "date": props["Match Date"]["date"]["start"] if props["Match Date"]["date"] else "",
                    "league": props["League"]["select"]["name"] if props.get("League") and props["League"]["select"] else "",
                    "competition": props["Competition"]["select"]["name"] if props["Competition"]["select"] else "",
                    "home_away": props["Home/Away"]["select"]["name"] if props["Home/Away"]["select"] else "",
                    "venue": props["Venue"]["rich_text"][0]["text"]["content"] if props["Venue"]["rich_text"] else "",
                    "broadcast": props["Broadcast"]["select"]["name"] if props.get("Broadcast") and props["Broadcast"]["select"] else "",
                }
                matches.append(match)
            
            print(f"   ✅ Found {len(matches)} match(es) today")
            return matches
            
        except Exception as e:
            print(f"   ❌ Error fetching matches: {e}")
            return []
    
    def format_match_time(self, date_str):
        """Format match datetime for display in EST."""
        try:
            # Parse the datetime (usually in UTC)
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Convert to EST (Eastern Time)
            est = pytz.timezone('America/New_York')
            dt_est = dt.astimezone(est)
            
            # Format as 12-hour time with AM/PM
            return dt_est.strftime("%I:%M %p EST")
        except:
            return "Time TBD"
    
    def format_match_short(self, match):
        """Format a match for short display."""
        time = self.format_match_time(match['date'])
        return f"{match['team']} vs {match['opponent']} at {time}"
    
    def create_match_message(self, match):
        """Create SMS message for a single match."""
        time = self.format_match_time(match['date'])
        message = f"⚽ GAME DAY!\n{match['team']} vs {match['opponent']}\n🕐 {time}"

        if match['venue']:
            message += f"\n📍 {match['venue']}"

        if match['broadcast']:
            message += f"\n📺 {match['broadcast']}"

        if match['league']:
            message += f"\n🏆 {match['league']}"

        return message
    
    def send_notifications(self, preview=False):
        """
        Check for today's matches and send notifications.
        
        Args:
            preview: If True, show message without sending
        """
        print("=" * 60)
        print("🔔 Game Day Notification Check")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        
        matches = self.get_today_matches()
        
        if not matches:
            print("\n✅ No matches scheduled for today")
            print("   No notifications sent.")
            return
        
        # Show matches found
        print("\n📋 Today's Matches:")
        for i, match in enumerate(matches, 1):
            print(f"   {i}. {self.format_match_short(match)}")
        
        if preview:
            print("\n📱 Message Preview:")
            for i, match in enumerate(matches, 1):
                msg = self.create_match_message(match)
                print(f"\n--- Message {i} ({len(msg)} chars) ---")
                print(msg)
            print("\n⚠️  Preview mode - no SMS sent")
            return

        # Send one SMS per match
        print("\n📱 Sending SMS notifications...")
        all_sent = True
        for match in matches:
            msg = self.create_match_message(match)
            if not send_text(msg):
                all_sent = False

        if all_sent:
            print(f"\n✅ {len(matches)} notification(s) sent successfully!")
        else:
            print("\n❌ One or more notifications failed to send")
    
    def send_test_message(self):
        """Send a test message to verify SMS is working."""
        print("=" * 60)
        print("🧪 Sending Test Message")
        print("=" * 60)
        
        test_message = f"⚽ Soccer Tracker Test\n\nSMS notifications are working!\n\nSent at {datetime.now().strftime('%I:%M %p on %B %d, %Y')}"
        
        print(f"\n📱 Test message:\n{test_message}\n")
        
        success = send_text(test_message)
        
        if success:
            print("\n✅ Test message sent! Check your phone.")
        else:
            print("\n❌ Test failed. Check your .env configuration.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Send SMS notifications for today's soccer matches"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Send test message"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview message without sending"
    )
    
    args = parser.parse_args()
    
    # Load and verify environment variables
    load_dotenv()
    required_vars = ["NOTION_TOKEN", "NOTION_DATABASE_ID", "EMAIL_FROM", "EMAIL_PASSWORD", "SMS_RECIPIENTS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file.")
        return
    
    try:
        notifier = GameDayNotifier()
        
        if args.test:
            notifier.send_test_message()
        else:
            notifier.send_notifications(preview=args.preview)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()