# Daily Money Brief

Automated daily Gen Z finance brief for TikTok content. Runs every morning at 9 AM EST via GitHub Actions.

## What it does
- Claude researches today's top 5 money stories impacting young people
- Writes simple explanations a 6th grader can understand
- Includes TikTok angles and opening lines
- Emails the brief to you every morning

## Setup
Add these secrets to the repo (Settings → Secrets → Actions):

1. `ANTHROPIC_API_KEY` — Your Claude API key from console.anthropic.com
2. `GMAIL_USERNAME` — The Gmail address to send FROM (e.g. yourname@gmail.com)
3. `GMAIL_APP_PASSWORD` — A Gmail App Password (NOT your regular password)

### How to get a Gmail App Password:
1. Go to myaccount.google.com
2. Security → 2-Step Verification (enable it if not already)
3. At the bottom: App Passwords
4. Create one for "Mail" → "Other" → name it "Daily Brief"
5. Copy the 16-character password → paste as `GMAIL_APP_PASSWORD` secret

## Test it
Go to Actions tab → "Daily Gen Z Money Brief" → "Run workflow" → click the green button.

## Change the schedule
Edit `.github/workflows/daily-brief.yml` line 4. The cron is in UTC:
- `0 13 * * *` = 9 AM EST (during EDT/summer)
- `0 14 * * *` = 9 AM EST (during EST/winter)
