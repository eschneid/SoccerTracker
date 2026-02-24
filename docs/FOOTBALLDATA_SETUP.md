# ⚽ Football-Data.org API Setup Guide

This guide will help you set up Football-Data.org API for tracking Manchester United, Manchester City, and Borussia Dortmund with **FREE, CURRENT SEASON DATA**.

## 🎯 Why Football-Data.org?

**Free Tier Includes:**
- ✅ **Premier League** (Manchester United, Manchester City)
- ✅ **Bundesliga** (Borussia Dortmund)
- ✅ **10+ major European competitions** (Champions League, La Liga, Serie A, etc.)
- ✅ **10 API calls per minute** (14,400/day)
- ✅ **Current season data** (2025/26)
- ✅ **FREE FOREVER** - No credit card required!

**Not Included:**
- ❌ MLS (not covered by this API)
- ❌ NWSL (not covered by this API)

## 🚀 Step 1: Sign Up

1. Go to: **https://www.football-data.org/client/register**
2. Fill out the registration form:
   - Name
   - Email address
   - Use case (select "Hobby project" or "Education")
3. Click **"Register"**
4. Check your email for the API key

## 🔑 Step 2: Get Your API Key

After registration, you'll receive an email with:
- ✅ Your **API key** (a long string of letters and numbers)
- ✅ API documentation link

**Important:** Save this API key! You'll need it for your `.env` file.

## 📝 Step 3: Update Your .env File

Add your Football-Data.org API key to your `.env` file:

```bash
# Football-Data.org API
FOOTBALLDATA_API_KEY=your_api_key_here

# Keep your existing Notion credentials
NOTION_TOKEN=
NOTION_DATABASE_ID=

# You can remove these (no longer needed)
# API_FOOTBALL_KEY=...
# SPORTMONKS_API_KEY=...

# Twilio credentials (for SMS - set up later)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
MY_PHONE_NUMBER=+1234567890
WIFE_PHONE_NUMBER=+1234567890

# Optional: Favorite teams for personalized messages
MY_FAVORITE_TEAM=Manchester United
WIFE_FAVORITE_TEAM=Borussia Dortmund
```

## 🧪 Step 4: Test the Script

```powershell
python sync_matches_footballdata.py
```

You should see:
```
============================================================
⚽ Soccer Match Sync (Football-Data.org)
============================================================
Started at: 2026-02-14 16:00:00

🔍 Fetching fixtures for Manchester United...
   Date range: 2026-02-07 to 2026-03-16
   Team ID: 66
   ✅ Found 3 fixtures
   ✅ Created: Manchester United vs Liverpool
   ✅ Created: Manchester United vs Arsenal
   ...

🔍 Fetching fixtures for Manchester City...
   ✅ Found 2 fixtures
   ...

🔍 Fetching fixtures for Borussia Dortmund...
   ✅ Found 3 fixtures
   ...

============================================================
✅ Sync Complete!
============================================================
```

## 📊 Team IDs Reference

Pre-configured teams:

| Team | Team ID | League | Competition Code |
|------|---------|--------|------------------|
| Manchester United | 66 | Premier League | PL |
| Manchester City | 65 | Premier League | PL |
| Borussia Dortmund | 4 | Bundesliga | BL1 |

## ➕ Adding More Teams

Want to add Arsenal, Bayern Munich, or other teams?

### Finding Team IDs:

**Method 1: Check the Football-Data.org website**
- Browse teams in competitions: https://www.football-data.org/

**Method 2: Use the API**
Search for a team by name:
```bash
curl -X GET "https://api.football-data.org/v4/teams?name=TEAM_NAME" \
  -H "X-Auth-Token: YOUR_API_KEY"
```

**Method 3: Common Team IDs**
- Arsenal: 57
- Chelsea: 61
- Liverpool: 64
- Tottenham: 73
- Bayern Munich: 5
- Real Madrid: 86
- Barcelona: 81

### Adding a New Team:

1. Edit `sync_matches_footballdata.py`
2. Add to the `self.teams` dictionary:

```python
self.teams = {
    "Manchester United": {
        "id": 66,
        "competition_code": "PL",
        "notion_season": "2025/26"
    },
    "Manchester City": {
        "id": 65,
        "competition_code": "PL",
        "notion_season": "2025/26"
    },
    "Borussia Dortmund": {
        "id": 4,
        "competition_code": "BL1",
        "notion_season": "2025/26"
    },
    "Arsenal": {  # NEW TEAM
        "id": 57,
        "competition_code": "PL",
        "notion_season": "2025/26"
    }
}
```

3. Add the team to your Notion database's Team select options

## 🔄 Updating Your Scheduler

Update `scheduler.py` to use the new script:

```python
def daily_sync(self):
    """Run the daily match data sync."""
    self.log("=" * 60)
    self.log("🔄 Starting Daily Sync")
    self.log("=" * 60)
    self.run_script("sync_matches_footballdata.py")  # Changed this line
```

Or if using Windows Task Scheduler:
- Edit your task
- Change script path to: `sync_matches_footballdata.py`

## 📊 Rate Limits

**Football-Data.org Free Tier:**
- **10 requests per minute**
- That equals **14,400 requests per day**
- More than enough for your use case!

**Current Usage:**
- 3 teams × 3 syncs per day = 9 requests
- Well within limits! ✅

## 🔧 Troubleshooting

### "Missing FOOTBALLDATA_API_KEY"
- Make sure you added it to `.env` file
- Check for typos (no spaces around `=`)
- Restart terminal/PowerShell

### "Access forbidden" (403 error)
- You might be trying to access a competition not in free tier
- Free tier includes: PL, BL1, CL, EL, PD, SA, FL1, EC, PPL, BSA, WC
- MLS is NOT included in free tier

### "Rate limit exceeded" (429 error)
- You're making more than 10 requests/minute
- The script includes 1-2 second delays
- Wait a minute and try again

### "No fixtures found"
- Team ID might be wrong
- Date range might not include matches
- Check if the season has started

### "Could not find database"
- Notion issue (not Football-Data.org related)
- Make sure database is shared with integration
- Verify NOTION_DATABASE_ID is correct

## 🆚 API Comparison

| Feature | API-Football Free | Football-Data.org Free |
|---------|-------------------|------------------------|
| **Requests/Day** | 100 | 14,400 (10/min) |
| **Premier League** | 2022-2024 only | ✅ Current season |
| **Bundesliga** | 2022-2024 only | ✅ Current season |
| **MLS** | ❌ Paid only | ❌ Not available |
| **Current Season** | ❌ Paid only | ✅ FREE |
| **Data Quality** | Excellent | Excellent |
| **Sign Up** | Instant | Email verification |

## 🎉 What You Get

With Football-Data.org, you now have:

✅ **Manchester United** fixtures (current season)
✅ **Manchester City** fixtures (current season)  
✅ **Borussia Dortmund** fixtures (current season)
✅ **Champions League** if any of your teams qualify
✅ **FA Cup, DFB Pokal** cup competitions
✅ All synchronized to Notion automatically
✅ 100% FREE forever

## 🚫 MLS & NWSL Workaround

Since MLS and NWSL aren't available, you have options:

**Option 1: Manual Entry**
- Check schedules at mlssoccer.com or nwslsoccer.com
- Add games manually to Notion database

**Option 2: Simple Web Scraper** (I can create this)
- Scrapes MLS/NWSL websites
- Adds to Notion automatically
- Requires more setup

**Option 3: Paid API**
- API-Football or SportsDataIO (~$40-70/month)
- Includes MLS and other US leagues

## ✅ Next Steps

1. ✅ Sign up for Football-Data.org
2. ✅ Add API key to `.env`
3. ✅ Test the script
4. ✅ Update your scheduler
5. 🔜 Set up Twilio for SMS notifications
6. 🔜 Decide on MLS solution (manual vs scraper vs paid)

---

**Great choice on Football-Data.org!** It's reliable, well-documented, and truly free. Your Premier League and Bundesliga tracking is now set up with current season data! 🎉
