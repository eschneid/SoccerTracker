# ⚽ Soccer Schedule Tracker - Notion Database Setup

This project creates a Notion database to track soccer team schedules, results, and sends SMS notifications for your favorite teams (Manchester United & Columbus Crew).

## 📋 Quick Start Guide

### Step 1: Set Up Notion Integration

1. **Create a Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click **"+ New integration"**
   - Name it (e.g., "Soccer Tracker")
   - Select the workspace where you want the database
   - Click **Submit**
   - Copy the **"Internal Integration Token"** (starts with `secret_...`)

2. **Prepare Your Notion Page:**
   - Open Notion and create a new page (or use an existing one)
   - This will be the parent page for your database
   - Copy the page ID from the URL:
     - URL format: `https://notion.so/workspace/PAGE_ID?v=...`
     - The PAGE_ID is the 32-character string (with or without dashes)

3. **Share Page with Integration:**
   - On your Notion page, click the **"..."** menu (top right)
   - Click **"Add connections"**
   - Select your integration (e.g., "Soccer Tracker")
   - Click **"Confirm"**

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 3: Run the Database Creator

**Option A: Interactive Mode**
```bash
python create_notion_soccer_db.py
```
The script will prompt you for:
- Notion integration token
- Parent page ID

**Option B: Using Environment Variables**
```bash
# Create a .env file
echo "NOTION_TOKEN=your_token_here" > .env
echo "NOTION_PAGE_ID=your_page_id_here" >> .env

# Run the script
python create_notion_soccer_db.py
```

### Step 4: Verify Setup

After running the script:
1. Check your Notion page - you should see a new database titled "⚽ Soccer Schedule Tracker"
2. The database will have all necessary fields (Team, Opponent, Match Date, etc.)
3. If you chose to add samples, you'll see 2 example matches
4. Your `.env` file will now contain the `NOTION_DATABASE_ID`

## 🗄️ Database Schema

Your Notion database will have these properties:

| Property | Type | Description |
|----------|------|-------------|
| **Opponent** | Title | The opposing team name |
| **Team** | Select | Your team (Manchester United or Columbus Crew) |
| **Match Date** | Date | When the match takes place |
| **Competition** | Select | Premier League, MLS, FA Cup, etc. |
| **Home/Away** | Select | Home, Away, or Neutral |
| **Result** | Select | Win, Loss, Draw, or Upcoming |
| **Score** | Text | Final score (e.g., "2-1") |
| **Goals For** | Number | Goals scored by your team |
| **Goals Against** | Number | Goals conceded |
| **Status** | Select | Scheduled, Live, Completed, etc. |
| **Venue** | Text | Stadium name |
| **Season** | Select | 2024/25 or 2025 |
| **Match ID** | Text | API reference ID |
| **Last Updated** | Date | Last sync timestamp |
| **Notes** | Text | Additional information |

## 🔧 Troubleshooting

### "Could not find database with ID"
- Make sure you shared the **page** (not the database) with your integration
- The page ID should be from the parent page, not the database

### "Unauthorized" Error
- Verify your integration token is correct
- Make sure it starts with `secret_`
- Check that the integration has access to the workspace

### "Invalid parent"
- Ensure the page ID is 32 characters
- Remove any dashes if present (the script does this automatically)
- Make sure the page exists and you have access

## 📝 Next Steps

After creating the database, you can:

1. **Customize Teams:** Add more teams to the "Team" select property
2. **Add Competitions:** Include additional competitions you follow
3. **Manual Entries:** Add upcoming matches manually
4. **API Integration:** Set up the automated sync script (coming next!)
5. **SMS Notifications:** Configure Twilio for match reminders

## 🔐 Security Notes

- **Never commit your `.env` file** to version control
- Add `.env` to your `.gitignore`
- Keep your Notion token secure
- Regenerate tokens if they're exposed

## 📦 Files in This Project

- `create_notion_soccer_db.py` - Database creation script
- `requirements.txt` - Python dependencies
- `README.md` - This file
- `.env` - Your credentials (created automatically, gitignored)

## 🚀 Coming Soon

- API integration script to fetch match data
- Automated daily sync
- SMS notification system
- Weekly match preview texts
- Game day reminder system

---

**Questions?** Feel free to modify the database properties to fit your needs!
** keep alive **
