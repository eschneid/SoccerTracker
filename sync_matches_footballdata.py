#!/usr/bin/env python3
"""
Soccer Schedule Sync Script (Football-Data.org API)

This script fetches match data from Football-Data.org and syncs it to your Notion database.
Supports Premier League (Man United, Man City) and Bundesliga (Borussia Dortmund)

Prerequisites:
    - Notion database created (run create_notion_soccer_db.py first)
    - Football-Data.org API key (get free at https://www.football-data.org/client/register)
    - All credentials in .env file

Usage:
    python sync_matches_footballdata.py
"""

import os
import requests
from datetime import datetime, timedelta
from notion_client import Client
from dotenv import load_dotenv
import time


class FootballDataSync:
    """Syncs soccer match data from Football-Data.org to Notion."""
    
    def __init__(self):
        """Initialize API clients and load configuration."""
        load_dotenv()
        
        # Notion setup
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        # Football-Data.org API setup
        self.api_key = os.getenv("FOOTBALLDATA_API_KEY")
        self.api_base_url = "https://api.football-data.org/v4"
        self.api_headers = {
            "X-Auth-Token": self.api_key
        }
        
        # Team configuration with Football-Data.org team IDs
        self.teams = {
            "Manchester United": {
                "id": 66,  # Football-Data.org team ID
                "competition_code": "PL",  # Premier League
                "league": "Premier League",
                "notion_season": "2025/26"
            },
            "Manchester City": {
                "id": 65,  # Football-Data.org team ID
                "competition_code": "PL",  # Premier League
                "league": "Premier League",
                "notion_season": "2025/26"
            },
            "Borussia Dortmund": {
                "id": 4,  # Football-Data.org team ID
                "competition_code": "BL1",  # Bundesliga
                "league": "Bundesliga",
                "notion_season": "2025/26"
            },
            "Brentford FC": {
                "id": 402,  # Football-Data.org team ID
                "competition_code": "PL",  # Bundesliga
                "league": "Premier League",
                "notion_season": "2025/26"
            }
        }
        
        # ESPN API setup (no key required)
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer"

        # NWSL teams tracked via ESPN
        self.nwsl_teams = {
            "Racing Louisville FC": {
                "espn_id": 20905,
                "league": "NWSL",
                "notion_season": str(datetime.now().year)
            }
        }

        # Competition mapping
        self.competition_map = {
            "PL": "Premier League",
            "ELC": "Championship",
            "CL": "Champions League",
            "CLI": "Champions League",
            "EL": "Europa League",
            "EC": "Europa Conference League",
            "FAC": "FA Cup",
            "EFL": "League Cup",
            "BL1": "Bundesliga",
            "DFB": "DFB Pokal",
            "WC": "World Cup",
        }
    
    def make_request(self, endpoint, params=None):
        """
        Make a request to Football-Data.org API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            dict: API response data
        """
        url = f"{self.api_base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.api_headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                print(f"   ⚠️  Access forbidden - this competition may not be in your plan")
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limit exceeded - wait a minute")
            else:
                print(f"   ❌ HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Request error: {e}")
            return None
    
    def fetch_espn_team_schedule(self, team_name):
        """Fetch NWSL schedule for a team from the ESPN API, returning raw events."""
        team_config = self.nwsl_teams[team_name]
        espn_id = team_config["espn_id"]
        season = datetime.now().year
        url = f"{self.espn_base_url}/usa.nwsl/teams/{espn_id}/schedule?season={season}"

        print(f"\n🔍 Fetching ESPN schedule for {team_name} (season {season})...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            events = data.get("events", [])
            print(f"   ✅ Found {len(events)} fixtures")
            return events
        except Exception as e:
            print(f"   ❌ ESPN request error: {e}")
            return []

    def parse_espn_fixture(self, event, team_name):
        """Parse an ESPN event into Notion-friendly format."""
        team_config = self.nwsl_teams[team_name]
        espn_id = team_config["espn_id"]

        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])

        # Identify home/away and opponent
        our_team = next((c for c in competitors if str(c.get("id")) == str(espn_id)), None)
        opponent_entry = next((c for c in competitors if str(c.get("id")) != str(espn_id)), None)
        is_home = our_team.get("homeAway") == "home" if our_team else True
        opponent_name = opponent_entry.get("team", {}).get("displayName", "Unknown") if opponent_entry else "Unknown"

        # Scores — ESPN returns score as a dict {"value": 2, "displayValue": "2"} or plain string
        def extract_score(competitor):
            if competitor is None:
                return None
            s = competitor.get("score")
            if s is None:
                return None
            if isinstance(s, dict):
                return s.get("value")
            return s

        our_score = extract_score(our_team)
        opp_score = extract_score(opponent_entry)

        # Status
        status_state = competition.get("status", {}).get("type", {}).get("state", "pre")
        status_name = competition.get("status", {}).get("type", {}).get("name", "STATUS_SCHEDULED")
        espn_status_map = {
            "STATUS_SCHEDULED": "Scheduled",
            "STATUS_IN_PROGRESS": "Live",
            "STATUS_FINAL": "Completed",
            "STATUS_POSTPONED": "Postponed",
            "STATUS_CANCELED": "Cancelled",
            "STATUS_SUSPENDED": "Postponed",
        }
        notion_status = espn_status_map.get(status_name, "Scheduled")

        # Result
        result = "Upcoming"
        if status_state == "post" and our_score is not None and opp_score is not None:
            our_score_int = int(our_score)
            opp_score_int = int(opp_score)
            if our_score_int > opp_score_int:
                result = "Win"
            elif our_score_int < opp_score_int:
                result = "Loss"
            else:
                result = "Draw"

        # Score string
        score = ""
        if our_score is not None and opp_score is not None:
            score = f"{our_score}-{opp_score}"

        # Broadcast — prefer TV over streaming
        broadcasts = competition.get("broadcasts", [])
        broadcast = None
        for b in sorted(broadcasts, key=lambda x: (x.get("type") != "TV")):
            name = b.get("media", {}).get("shortName") or b.get("names", [None])[0]
            if name:
                broadcast = name
                break

        # Venue
        venue_data = competition.get("venue", {})
        venue = venue_data.get("fullName", "TBD")

        # Date
        match_date = event.get("date", "")

        goals_for = int(our_score) if our_score is not None else None
        goals_against = int(opp_score) if opp_score is not None else None

        return {
            "team": team_name,
            "opponent": opponent_name,
            "match_date": match_date,
            "league": team_config["league"],
            "competition": "NWSL",
            "home_away": "Home" if is_home else "Away",
            "result": result,
            "score": score,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "status": notion_status,
            "venue": venue,
            "season": team_config["notion_season"],
            "match_id": f"espn-{event.get('id', '')}",
            "broadcast": broadcast,
        }

    def sync_nwsl_team(self, team_name):
        """Sync all fixtures for an NWSL team via ESPN."""
        events = self.fetch_espn_team_schedule(team_name)
        for event in events:
            match_data = self.parse_espn_fixture(event, team_name)
            existing_page = self.find_existing_match(match_data["match_id"])
            if existing_page:
                self.update_notion_page(existing_page["id"], match_data)
            else:
                self.create_notion_page(match_data)
            time.sleep(0.5)

    def fetch_team_fixtures(self, team_name, days_back=7, days_forward=30):
        """
        Fetch fixtures for a specific team.
        
        Args:
            team_name: Name of the team
            days_back: Days in the past to fetch
            days_forward: Days in the future to fetch
            
        Returns:
            list: List of fixture dictionaries
        """
        team_config = self.teams[team_name]
        team_id = team_config["id"]
        
        # Calculate date range
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        date_to = (datetime.now() + timedelta(days=days_forward)).strftime("%Y-%m-%d")
        
        print(f"\n🔍 Fetching fixtures for {team_name}...")
        print(f"   Date range: {date_from} to {date_to}")
        print(f"   Team ID: {team_id}")
        
        # Football-Data.org endpoint for team matches
        endpoint = f"teams/{team_id}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to
        }
        
        data = self.make_request(endpoint, params)
        
        if data and 'matches' in data:
            fixtures = data['matches']
            print(f"   ✅ Found {len(fixtures)} fixtures")
            return fixtures
        else:
            print(f"   ⚠️  No fixtures found")
            return []
    
    def parse_fixture(self, fixture, team_name):
        """
        Parse Football-Data.org fixture data into Notion-friendly format.
        
        Args:
            fixture: Raw fixture data from Football-Data.org
            team_name: Name of the team we're tracking
            
        Returns:
            dict: Parsed fixture data
        """
        team_config = self.teams[team_name]
        team_id = team_config["id"]
        
        # Get teams
        home_team = fixture.get('homeTeam', {})
        away_team = fixture.get('awayTeam', {})
        
        # Determine if home or away
        is_home = home_team.get('id') == team_id
        opponent_name = away_team.get('name', 'Unknown') if is_home else home_team.get('name', 'Unknown')
        
        # Get scores
        score_data = fixture.get('score', {})
        fulltime = score_data.get('fullTime', {})
        home_score = fulltime.get('home')
        away_score = fulltime.get('away')
        
        # Calculate result
        result = "Upcoming"
        status = fixture.get('status', 'SCHEDULED')
        
        if status in ['FINISHED', 'AWARDED']:
            if home_score is not None and away_score is not None:
                if is_home:
                    if home_score > away_score:
                        result = "Win"
                    elif home_score < away_score:
                        result = "Loss"
                    else:
                        result = "Draw"
                else:
                    if away_score > home_score:
                        result = "Win"
                    elif away_score < home_score:
                        result = "Loss"
                    else:
                        result = "Draw"
        
        # Status mapping
        status_map = {
            'SCHEDULED': 'Scheduled',
            'TIMED': 'Scheduled',
            'IN_PLAY': 'Live',
            'PAUSED': 'Live',
            'FINISHED': 'Completed',
            'AWARDED': 'Completed',
            'POSTPONED': 'Postponed',
            'CANCELLED': 'Cancelled',
            'SUSPENDED': 'Postponed',
        }
        
        notion_status = status_map.get(status, 'Scheduled')
        
        # Competition name
        competition = fixture.get('competition', {})
        competition_code = competition.get('code', '')
        competition_name = self.competition_map.get(competition_code, competition.get('name', 'Unknown'))
        
        # Build score string
        score = ""
        if home_score is not None and away_score is not None:
            score = f"{home_score}-{away_score}" if is_home else f"{away_score}-{home_score}"
        
        # Venue - Football-Data.org doesn't always provide this
        venue = "TBD"
        
        # Match date - convert from UTC
        match_date = fixture.get('utcDate', '')
        
        parsed = {
            "team": team_name,
            "opponent": opponent_name,
            "match_date": match_date,
            "league": team_config["league"],
            "competition": competition_name,
            "home_away": "Home" if is_home else "Away",
            "result": result,
            "score": score,
            "goals_for": home_score if is_home else away_score,
            "goals_against": away_score if is_home else home_score,
            "status": notion_status,
            "venue": venue,
            "season": team_config["notion_season"],
            "match_id": str(fixture.get('id', '')),
            "broadcast": None,
        }

        return parsed
    
    def find_existing_match(self, match_id):
        """
        Check if a match already exists in Notion.
        
        Args:
            match_id: The Football-Data.org fixture ID
            
        Returns:
            dict or None: Notion page if found
        """
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Match ID",
                    "rich_text": {
                        "equals": match_id
                    }
                }
            )
            
            if results["results"]:
                return results["results"][0]
            return None
            
        except Exception as e:
            print(f"   ⚠️  Error checking existing match: {e}")
            return None
    
    def create_notion_page(self, match_data):
        """Create a new match entry in Notion."""
        try:
            properties = {
                "Team": {"select": {"name": match_data["team"]}},
                "Opponent": {"title": [{"text": {"content": match_data["opponent"]}}]},
                "Match Date": {"date": {"start": match_data["match_date"]}},
                "League": {"select": {"name": match_data["league"]}},
                "Competition": {"select": {"name": match_data["competition"]}},
                "Home/Away": {"select": {"name": match_data["home_away"]}},
                "Result": {"select": {"name": match_data["result"]}},
                "Status": {"select": {"name": match_data["status"]}},
                "Venue": {"rich_text": [{"text": {"content": match_data["venue"]}}]},
                "Season": {"select": {"name": match_data["season"]}},
                "Match ID": {"rich_text": [{"text": {"content": match_data["match_id"]}}]},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}}
            }
            
            # Add score data if available
            if match_data["score"]:
                properties["Score"] = {"rich_text": [{"text": {"content": match_data["score"]}}]}

            if match_data["goals_for"] is not None:
                properties["Goals For"] = {"number": match_data["goals_for"]}

            if match_data["goals_against"] is not None:
                properties["Goals Against"] = {"number": match_data["goals_against"]}

            if match_data.get("broadcast"):
                properties["Broadcast"] = {"select": {"name": match_data["broadcast"]}}

            self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            print(f"   ✅ Created: {match_data['team']} vs {match_data['opponent']}")
            
        except Exception as e:
            print(f"   ❌ Error creating page: {e}")
    
    def update_notion_page(self, page_id, match_data):
        """Update an existing match entry in Notion."""
        try:
            properties = {
                "Match Date": {"date": {"start": match_data["match_date"]}},
                "Result": {"select": {"name": match_data["result"]}},
                "Status": {"select": {"name": match_data["status"]}},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}}
            }
            
            # Update score data if available
            if match_data["score"]:
                properties["Score"] = {"rich_text": [{"text": {"content": match_data["score"]}}]}

            if match_data["goals_for"] is not None:
                properties["Goals For"] = {"number": match_data["goals_for"]}

            if match_data["goals_against"] is not None:
                properties["Goals Against"] = {"number": match_data["goals_against"]}

            if match_data.get("broadcast"):
                properties["Broadcast"] = {"select": {"name": match_data["broadcast"]}}

            self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            print(f"   🔄 Updated: {match_data['team']} vs {match_data['opponent']}")
            
        except Exception as e:
            print(f"   ❌ Error updating page: {e}")
    
    def sync_team(self, team_name):
        """Sync all fixtures for a specific team."""
        fixtures = self.fetch_team_fixtures(team_name)
        
        for fixture in fixtures:
            match_data = self.parse_fixture(fixture, team_name)
            existing_page = self.find_existing_match(match_data["match_id"])
            
            if existing_page:
                self.update_notion_page(existing_page["id"], match_data)
            else:
                self.create_notion_page(match_data)
            
            # Small delay to respect API rate limits (10 req/min = 6 sec between)
            time.sleep(1)
    
    def sync_all_teams(self):
        """Sync fixtures for all configured teams."""
        print("=" * 60)
        print("⚽ Soccer Match Sync (Football-Data.org)")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for team_name in self.teams.keys():
            self.sync_team(team_name)
            time.sleep(2)

        for team_name in self.nwsl_teams.keys():
            self.sync_nwsl_team(team_name)
            time.sleep(2)

        print("\n" + "=" * 60)
        print("✅ Sync Complete!")
        print("=" * 60)


def main():
    """Main function to run the sync."""
    # Load environment variables FIRST
    load_dotenv()
    
    # Verify environment variables
    required_vars = ["NOTION_TOKEN", "NOTION_DATABASE_ID", "FOOTBALLDATA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease update your .env file with these values.")
        print("\nTo get Football-Data.org API key:")
        print("1. Sign up at https://www.football-data.org/client/register")
        print("2. Verify your email")
        print("3. Check your email for the API key")
        return
    
    try:
        syncer = FootballDataSync()
        syncer.sync_all_teams()
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()