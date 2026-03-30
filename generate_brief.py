"""
Daily Gen Z Money Brief Generator
Uses Claude API with web search to find today's top finance stories.
Posts as a GitHub Issue + emails to sharrank@budgetcaddie.com.
"""

import os
import json
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta
import anthropic

def get_recent_headlines():
    """Pull headlines from the last 7 days of issues to avoid repeats."""
    try:
        result = subprocess.run(
            ["gh", "issue", "list",
             "--repo", os.environ.get("GITHUB_REPOSITORY", "Sharranrae/daily-money-brief"),
             "--label", "daily-brief",
             "--limit", "7",
             "--json", "body",
             "--jq", ".[].body"],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            # Extract headlines from past briefs
            lines = result.stdout.strip().split("\n")
            headlines = [l.strip() for l in lines if l.strip().startswith("HEADLINE:")]
            return headlines[:35]  # max 35 recent headlines (7 days × 5)
    except Exception:
        pass
    return []


def generate_brief():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    est = timezone(timedelta(hours=-4))
    today = datetime.now(est).strftime("%B %d, %Y")

    # Get recent headlines to avoid repeats
    recent = get_recent_headlines()
    avoid_block = ""
    if recent:
        avoid_list = "\n".join(f"- {h}" for h in recent)
        avoid_block = f"""

IMPORTANT — DO NOT REPEAT THESE STORIES. I already covered them this week:
{avoid_list}

Find completely DIFFERENT stories. New angles, new topics, new sources."""

    prompt = f"""Today is {today}. Find the top 5 money and finance news stories from today or this week that impact young people (ages 18-28).{avoid_block}

These can be ANYTHING related to money:
- Gas prices going up or down
- Netflix, Spotify, or any subscription raising prices
- Grocery/food costs changing
- A stock blowing up that Gen Z cares about (Tesla, Nvidia, meme stocks)
- Student loan news
- Housing/rent changes
- Job market shifts (layoffs, hiring booms)
- Crypto moves
- New financial products or apps
- Government policy affecting young people
- Inflation, interest rates
- Viral money stories on social media
- Side hustle trends
- BNPL or credit card news
- Tariffs, trade wars, economic policy

For each story, give me:

1. SOURCE LINK — The actual URL of the article you found this from. I need the real link so I can green screen it on TikTok.
2. HEADLINE — one punchy line (TikTok hook)
3. WHAT HAPPENED — 2-3 sentences. Explain it like you're telling a 6th grader. No jargon. Simple words.
4. WHY GEN Z SHOULD CARE — 1-2 sentences connecting it to a young person's wallet. Make it feel personal.
5. TIKTOK SCRIPT — The exact opening line I'd say to camera (2-3 sentences max). Make it sound natural, not scripted. Include the vibe in brackets: [funny] [shocking] [educational] [rant] [storytime]
6. LINKEDIN POST — Write a short LinkedIn post version of this story (3-5 sentences). Professional but relatable. Something a young finance creator would post. Use the brand voice "Today in Gen Z Finance". Start each post with "Today in Gen Z Finance:" and end with a question to drive engagement.

Format the email like this:

Subject line style: "Today in Gen Z Finance — {today}"

===========================
STORY 1
===========================
SOURCE: [full article URL]
HEADLINE: ...
WHAT HAPPENED: ...
WHY GEN Z SHOULD CARE: ...
TIKTOK SCRIPT: ...
LINKEDIN POST: ...

(repeat for all 5)

===========================
BONUS
===========================
One "did you know?" money fact I can use as a quick 15-second TikTok. Include the source link.

IMPORTANT: Every story MUST have a real, working source URL. I need to pull up the article on screen."""

    # Use Claude with web search enabled
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract text from response (may have multiple content blocks from tool use)
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    brief = "\n".join(text_parts)

    if not brief.strip():
        brief = "Brief generation returned empty. Check the workflow logs."

    return today, brief


def post_issue(today, brief):
    """Post the brief as a GitHub Issue using gh CLI."""
    title = f"Today in Gen Z Finance — {today}"

    # Write body to temp file to avoid shell escaping issues
    with open("/tmp/brief_body.md", "w") as f:
        f.write(brief)

    subprocess.run([
        "gh", "issue", "create",
        "--repo", os.environ.get("GITHUB_REPOSITORY", "Sharranrae/daily-money-brief"),
        "--title", title,
        "--body-file", "/tmp/brief_body.md",
        "--label", "daily-brief"
    ], check=True)


def send_email(today, brief):
    """Send the brief via Resend SDK."""
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("No RESEND_API_KEY set, skipping email.")
        return

    import resend
    resend.api_key = resend_key

    try:
        r = resend.Emails.send({
            "from": "Today in Gen Z Finance <brief@budgetcaddie.com>",
            "to": ["sharrank@budgetcaddie.com"],
            "subject": f"Today in Gen Z Finance — {today}",
            "text": brief
        })
        print(f"Email sent! ID: {r}")
    except Exception as e:
        print(f"Email failed: {e}")


if __name__ == "__main__":
    # Create label if it doesn't exist
    try:
        subprocess.run([
            "gh", "label", "create", "daily-brief",
            "--repo", os.environ.get("GITHUB_REPOSITORY", "Sharranrae/daily-money-brief"),
            "--color", "0E8A16",
            "--description", "Daily money brief"
        ], capture_output=True)
    except Exception:
        pass

    today, brief = generate_brief()
    print(f"Generated brief for {today}")
    print(brief[:500] + "...")
    post_issue(today, brief)
    print("Posted as GitHub Issue!")
    send_email(today, brief)
    print("Done!")
