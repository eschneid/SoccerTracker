# ⚽ Complete Soccer Tracker Setup Guide

This guide walks you through setting up the complete automated soccer tracking system with SMS notifications.

## 📋 Overview

Your system will:
1. **Daily at 6 AM**: Sync match data from API-Football to Notion
2. **Daily at 8 AM**: Send game day reminders for matches happening that day
3. **Sundays at 9 AM**: Send weekly preview of upcoming matches

## 🚀 Complete Setup Steps

### Step 1: Get Your API Keys

#### 1.1 Notion Integration
1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Name it: "Soccer Tracker"
4. Copy the **Integration Token** (starts with `secret_`)

#### 1.2 API-Football (Free Tier)
1. Go to https://www.api-football.com/
2. Click **"Sign Up"** (free tier: 100 requests/day)
3. Verify your email
4. Go to **Dashboard** → **My Access**
5. Copy your **API Key**

#### 1.3 Twilio (SMS Service)
1. Go to https://www.twilio.com/try-twilio
2. Sign up for free trial ($15 credit)
3. Get a phone number (verify it's SMS-capable)
4. From Console Dashboard, copy:
   - **Account SID**
   - **Auth Token**
   - **Your Twilio Phone Number**

### Step 2: Create Notion Database

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your NOTION_TOKEN and NOTION_PAGE_ID

# Create the database
python create_notion_soccer_db.py
```

After running this, your `.env` file will be updated with `NOTION_DATABASE_ID`.

### Step 3: Configure Environment Variables

Edit your `.env` file with all credentials:

```bash
# Notion
NOTION_TOKEN=secret_your_token_here
NOTION_PAGE_ID=your_page_id_here
NOTION_DATABASE_ID=will_be_filled_automatically

# API-Football
API_FOOTBALL_KEY=your_api_key_here

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Your phone numbers
MY_PHONE_NUMBER=+1234567890
WIFE_PHONE_NUMBER=+1234567890

# Favorite teams (optional, for personalized messages)
MY_FAVORITE_TEAM=Manchester United
WIFE_FAVORITE_TEAM=Columbus Crew
```

### Step 4: Test Each Component

#### Test Notion Sync
```bash
python sync_matches.py
```
This should fetch matches and add them to your Notion database.

#### Test SMS Notifications
```bash
python send_notifications.py --test
```
Both phone numbers should receive a test message.

#### Test Weekly Preview
```bash
python send_notifications.py --weekly
```

#### Test Game Day Reminder
```bash
python send_notifications.py --gameday
```

### Step 5: Run the Scheduler

#### Option A: Run Manually (Testing)
```bash
python scheduler.py
```
Press Ctrl+C to stop.

#### Option B: Run in Background (Linux/Mac)
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

To stop:
```bash
# Find the process ID
ps aux | grep scheduler.py

# Kill the process
kill <PID>
```

#### Option C: Set Up as System Service (Recommended for servers)
See **SYSTEMD_SERVICE.md** for instructions.

## 📱 SMS Message Examples

### Weekly Preview (Sunday 9 AM)
```
⚽ This Week's Soccer Schedule:

Manchester United:
• Saturday, Feb 15 at 12:30 PM
  Liverpool (Home) - Premier League

Columbus Crew:
• Sunday, Feb 16 at 04:00 PM
  FC Cincinnati (Away) - MLS Regular Season

⚽ Enjoy the matches!
```

### Game Day Reminder (8 AM on match day)
```
⚽ GAME DAY! ⚽

Manchester United vs Liverpool
Saturday, Feb 15 at 12:30 PM
📍 Old Trafford
🏆 Premier League

Let's go! 🔴⚪
```

## ⚙️ Customization

### Change Notification Times

Edit `scheduler.py` and modify these lines:

```python
# Daily sync at 6:00 AM
schedule.every().day.at("06:00").do(self.daily_sync)

# Game day reminders at 8:00 AM
schedule.every().day.at("08:00").do(self.gameday_reminder)

# Weekly preview on Sunday at 9:00 AM
schedule.every().sunday.at("09:00").do(self.weekly_preview)
```

### Add More Teams

Edit `sync_matches.py` and add teams to the `self.teams` dictionary:

```python
self.teams = {
    "Manchester United": {
        "id": 33,
        "league_id": 39,
        "season": 2024,
        "notion_season": "2024/25"
    },
    "Columbus Crew": {
        "id": 1614,
        "league_id": 253,
        "season": 2025,
        "notion_season": "2025"
    },
    # Add more teams here
}
```

To find team IDs:
1. Go to https://www.api-football.com/documentation-v3
2. Use the `/teams` endpoint
3. Search for your team

### Add More Competitions

Edit the `competition_map` in `sync_matches.py`:

```python
self.competition_map = {
    39: "Premier League",
    40: "FA Cup",
    253: "MLS Regular Season",
    # Add more here
}
```

### Customize SMS Messages

Edit the message templates in `send_notifications.py`:
- `send_weekly_preview()` - Weekly preview format
- `send_gameday_reminders()` - Game day reminder format

## 🔧 Troubleshooting

### "Unauthorized" from Notion
- Verify your integration token
- Make sure you shared the page with your integration
- Check that the database ID is correct

### "Invalid API Key" from API-Football
- Verify your API key is correct
- Check you haven't exceeded your quota (100 requests/day on free tier)
- Wait a few minutes if you just signed up

### SMS Not Sending
- Verify Twilio credentials
- Check phone numbers include country code (e.g., +1 for US)
- Verify your Twilio phone number is SMS-capable
- Check your Twilio account balance

### No Matches Found
- Verify team IDs are correct
- Check the season year is current
- Try expanding the date range in `sync_matches.py`

### Scheduler Not Running Tasks
- Check system time is correct
- Verify schedule times in `scheduler.py`
- Check logs for errors

## 💰 Cost Estimate

**Free Tier Usage:**
- **Notion**: Free
- **API-Football**: Free (100 requests/day limit)
- **Twilio Trial**: $15 credit
  - ~$0.0079 per SMS
  - Estimate: ~$5-10/month for 2 phones

**After Twilio Trial:**
- Pay-as-you-go: ~$0.0079/SMS
- Expected: $5-10/month for regular use

## 📊 API Rate Limits

**API-Football (Free Tier):**
- 100 requests per day
- The sync script is designed to stay well under this limit
- Typical usage: 2-4 requests/day (one per team)

**Notion API:**
- Rate limit: 3 requests/second
- The scripts include delays to respect this

**Twilio:**
- No practical rate limits for normal use
- Message queue handles delivery

## 🔄 Manual Operations

### Sync Now
```bash
python sync_matches.py
```

### Send Weekly Preview Now
```bash
python send_notifications.py --weekly
```

### Send Game Day Reminders Now
```bash
python send_notifications.py --gameday
```

### Send Test Message
```bash
python send_notifications.py --test
```

## 📝 Next Steps

Once everything is working:

1. **Set up automatic backups** of your `.env` file (securely!)
2. **Monitor the logs** to ensure everything runs smoothly
3. **Set up the systemd service** for automatic startup
4. **Add more teams** if you follow other clubs
5. **Customize the messages** to your preferences

## 🎉 You're All Set!

Your automated soccer tracker is now running. You'll receive:
- ✅ Weekly match previews every Sunday
- ✅ Game day reminders on match mornings
- ✅ Always up-to-date schedule in Notion

Enjoy never missing a match! ⚽
