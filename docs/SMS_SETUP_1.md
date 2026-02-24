# 📱 SMS Notifications Setup Guide (Email-to-SMS)

This guide shows you how to set up **FREE** SMS notifications using email-to-SMS gateways instead of Twilio.

## 🎯 Why Email-to-SMS?

**Advantages:**
- ✅ **100% FREE** - No Twilio costs!
- ✅ Works with existing Gmail/email account
- ✅ No credit card required
- ✅ Unlimited messages
- ✅ Works with all major carriers (Verizon, AT&T, T-Mobile, etc.)

**How it works:**
Each carrier provides an email address for each phone number. When you send an email to that address, it arrives as a text message on the phone.

## 📋 Email-to-SMS Gateway Addresses

Find your carrier's gateway:

| Carrier | Gateway Format | Example |
|---------|----------------|---------|
| **Verizon** | `NUMBER@vtext.com` | `@vtext.com` |
| **AT&T** | `NUMBER@txt.att.net` | `@txt.att.net` |
| **T-Mobile** | `NUMBER@tmomail.net` | `@tmomail.net` |
| **Sprint** | `NUMBER@messaging.sprintpcs.com` | `@messaging.sprintpcs.com` |
| **Google Fi** | `NUMBER@msg.fi.google.com` | `@msg.fi.google.com` |
| **Metro PCS** | `NUMBER@mymetropcs.com` | `@mymetropcs.com` |
| **Cricket** | `NUMBER@mms.cricketwireless.net` | `@mms.cricketwireless.net` |

**Don't see your carrier?** Google: "your carrier email to SMS gateway"

## 🚀 Step 1: Set Up Gmail App Password

Since you're using Gmail, you need an "App Password" (not your regular Gmail password):

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in to your Google account
3. Click **"Select app"** → Choose **"Mail"**
4. Click **"Select device"** → Choose **"Other"** → Type: "Soccer Tracker"
5. Click **"Generate"**
6. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)
7. Save it - you'll need this for your `.env` file

**Note:** If you don't see "App passwords" option:
- You may need to enable 2-factor authentication first
- Go to: https://myaccount.google.com/security
- Enable "2-Step Verification"
- Then try the app passwords link again

## 📝 Step 2: Update Your .env File

Add these lines to your `.env` file:

```bash
# Existing Notion config
NOTION_TOKEN=
NOTION_DATABASE_ID=

# Existing Football-Data.org config
FOOTBALLDATA_API_KEY=your_api_key_here

# SMS/Email Configuration (NEW)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
EMAIL_FROM=eschneid@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop

# Phone numbers (use carrier gateway addresses)
# Format: NUMBER@carrier-gateway.com
SMS_RECIPIENTS=@vtext.com, @vtext.com

# Send mode: "individual" (hidden) or "group" (all see each other)
SMS_SEND_MODE=group

# Optional: Favorite teams for personalized messages
MY_FAVORITE_TEAM=Manchester United
WIFE_FAVORITE_TEAM=Brentford FC
```

**Important:**
- Use your **Gmail app password** (not regular password)
- Use the correct **carrier gateway** for each phone number
- Remove spaces from phone numbers
- Separate multiple recipients with commas

## 🧪 Step 3: Test SMS

Test that SMS is working:

```powershell
python notify_gameday.py --test
```

You should receive a test message on both phones!

## 📅 Step 4: Test Game Day Check

Preview what would be sent (without actually sending):

```powershell
python notify_gameday.py --preview
```

Or send real notifications:

```powershell
python notify_gameday.py
```

## 🔄 Step 5: Set Up Automated Notifications

### Option A: Windows Task Scheduler (Recommended)

Create a task to check every morning at 8 AM:

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name: "Soccer Game Day Notifications"
4. Trigger: **Daily** at **8:00 AM**
5. Action: **Start a program**
   - Program: `C:\Path\To\Your\venv\Scripts\python.exe`
   - Arguments: `C:\Path\To\Your\Project\notify_gameday.py`
   - Start in: `C:\Path\To\Your\Project`
6. Click **Finish**

### Option B: Add to Your Scheduler Script

If you're using `scheduler.py`, add this function:

```python
def gameday_reminder(self):
    """Send game day reminders."""
    self.log("=" * 60)
    self.log("🔔 Checking for Game Day Reminders")
    self.log("=" * 60)
    self.run_script("notify_gameday.py")
```

And schedule it:

```python
# Game day reminders at 8:00 AM
schedule.every().day.at("08:00").do(self.gameday_reminder)
```

## 📱 Message Examples

### Game Day (8 AM):
```
⚽ GAME DAY! ⚽

Manchester United vs Liverpool
🕐 12:30 PM • 📍 Old Trafford
🏆 Premier League

Brentford FC vs Arsenal
🕐 03:00 PM • 📍 Gtech Community Stadium
🏆 Premier League
```

### Test Message:
```
⚽ Soccer Tracker Test

SMS notifications are working!

Sent at 08:00 AM on February 14, 2026
```

## 🔧 Troubleshooting

### "Authentication failed"
- Make sure you're using the **Gmail App Password**, not your regular password
- The password should be 16 characters with spaces: `abcd efgh ijkl mnop`
- Try removing spaces from the password in .env

### "No messages received"
- Verify you're using the correct carrier gateway
- Check that phone number has no spaces or dashes
- Try sending from Gmail directly to the gateway address to test
- Some carriers may block/filter email-to-SMS (rare)

### "Messages go to spam"
- This is normal for some carriers
- Recipients can add your email to contacts to prevent this

### "SMS_RECIPIENTS not found"
- Make sure there are no spaces around the `=` sign
- Example: `SMS_RECIPIENTS=number@vtext.com` (good)
- Example: `SMS_RECIPIENTS = number@vtext.com` (bad)

## 💰 Cost Comparison

| Method | Setup Cost | Monthly Cost | Per Message |
|--------|-----------|--------------|-------------|
| **Email-to-SMS** | FREE | FREE | FREE |
| **Twilio** | FREE | $1.15 | $0.0079 |

Email-to-SMS saves you **$5-10/month**! 💵

## 🎨 Customization

### Change Notification Time

Edit the scheduled time in Task Scheduler or `scheduler.py`:

```python
# Change from 8 AM to 7 AM
schedule.every().day.at("07:00").do(self.gameday_reminder)
```

### Personalize Messages

Set favorite teams in `.env`:

```bash
MY_FAVORITE_TEAM=Manchester United
WIFE_FAVORITE_TEAM=Brentford FC
```

### Group vs Individual Mode

```bash
# Group mode: All recipients see each other (like group text)
SMS_SEND_MODE=group

# Individual mode: Hidden from each other (like BCC)
SMS_SEND_MODE=individual
```

## ✅ Quick Test Checklist

- [ ] Created Gmail App Password
- [ ] Added to `.env` file
- [ ] Found carrier gateway addresses
- [ ] Tested with `python notify_gameday.py --test`
- [ ] Both phones received test message
- [ ] Set up automated daily check

## 🚀 You're All Set!

Now you'll get text notifications every morning when your teams play! ⚽📱

---

**No Twilio needed, no costs, just free texts!** 🎉
