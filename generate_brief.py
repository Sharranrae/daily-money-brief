"""
Daily Gen Z Money Brief Generator
Uses Claude API with web search to find today's top finance stories.
Posts as a GitHub Issue + emails to sharrank@budgetcaddie.com.
Second email: LinkedIn-ready post generated via Haiku (cheap).
"""

import os
import json
import subprocess
import urllib.request
import time
from datetime import datetime, timezone, timedelta
import anthropic


def get_recent_stories():
    """Pull headlines, topics, and sources from the last 7 days to avoid repeats."""
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
            lines = result.stdout.strip().split("\n")
            stories = []
            for l in lines:
                cleaned = l.strip().replace("**", "").replace("*", "")
                if cleaned.startswith("HEADLINE:"):
                    stories.append(cleaned)
                elif cleaned.startswith("SOURCE:"):
                    stories.append(cleaned)
                elif cleaned.startswith("WHAT HAPPENED:"):
                    # Grab first sentence as topic summary
                    stories.append(cleaned[:200])
            return stories[:100]
    except Exception:
        pass
    return []


def generate_brief():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    est = timezone(timedelta(hours=-4))
    today = datetime.now(est).strftime("%B %d, %Y")

    # Get recent stories to avoid repeats
    recent = get_recent_stories()
    avoid_block = ""
    if recent:
        avoid_list = "\n".join(f"- {h}" for h in recent)
        avoid_block = f"""

CRITICAL — DO NOT REPEAT ANY OF THESE TOPICS. I already covered them this week. This means:
- NO stories about gas prices or fuel costs
- NO stories about the SAVE student loan plan
- NO stories about entry-level job market struggles
- NO stories about Gen Z wealth surveys
- NO stories about Bitcoin/crypto price drops
- NO stories from any of the same sources/URLs listed below

Here are the exact headlines, sources, and summaries from my past briefs:
{avoid_list}

I need 5 COMPLETELY DIFFERENT TOPICS. Not the same story from a different outlet. Not a different angle on the same topic. Entirely new subjects I haven't covered."""

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

    # Use Claude with web search enabled (retry on overloaded errors)
    response = None
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
                messages=[{"role": "user", "content": prompt}]
            )
            break
        except anthropic.APIStatusError as e:
            if e.status_code != 529:
                raise
            wait = 30 * (attempt + 1)
            print(f"API overloaded (attempt {attempt + 1}/5). Retrying in {wait}s...")
            time.sleep(wait)
    if response is None:
        raise Exception("Claude API overloaded after 5 retries. Try again later.")

    # Extract text from response (may have multiple content blocks from tool use)
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    brief = "\n".join(text_parts)

    if not brief.strip():
        brief = "Brief generation returned empty. Check the workflow logs."

    return today, brief


def generate_linkedin_post(today, brief):
    """Take the full brief and reformat into a LinkedIn-ready post using Haiku (cheap)."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Here is today's finance brief with 5 stories. Reformat it into a single LinkedIn post I can copy and paste directly.

RULES:
- Headline: "5 Gen Z money stories you might have missed this week ({today})" followed by a down arrow emoji
- Number each story 1/ through 5/
- Each story gets 2-3 sentences MAX: what happened with real numbers, then why it matters to the reader personally. Make them feel it.
- Every fact and number must come directly from the brief below. Do NOT make up or change any statistics.
- Blank line between each numbered story
- After the 5 stories, end with exactly these three lines:

Follow me for daily breakdowns like this.
I break these down daily on my Substack. Link in the comments.
Download Budget Caddie on the App Store. Proactive AI that budgets, tracks, and coaches you before you overspend.

- No emojis anywhere in the post. Zero. Not in the headline, not in the stories, not in the CTAs.
- No hashtags
- No other closing lines
- NEVER use em dashes or en dashes (the long dash character). Use periods, commas, or just start a new sentence instead. Dashes are an AI giveaway.
- NEVER use fancy or uncommon words. No "jargon", "leverage", "nuanced", "landscape", "paradigm", "delve", "myriad", "robust", "tapestry", "realm", "foster", "utilize", "facilitate", "comprehensive", "moreover", "furthermore". Write like a normal 24 year old would talk.
- Output ONLY the LinkedIn post. Nothing else. No "here's the post" or any preamble.

THE BRIEF:
{brief}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    post = response.content[0].text.strip()
    return post


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
    """Send the full brief via Resend SDK."""
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
        print(f"Brief email sent! ID: {r}")
    except Exception as e:
        print(f"Brief email failed: {e}")


def send_linkedin_email(today, linkedin_post):
    """Send the LinkedIn post as a separate email."""
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        print("No RESEND_API_KEY set, skipping LinkedIn email.")
        return

    import resend
    resend.api_key = resend_key

    try:
        r = resend.Emails.send({
            "from": "Today in Gen Z Finance <brief@budgetcaddie.com>",
            "to": ["sharrank@budgetcaddie.com"],
            "subject": f"LinkedIn Post — {today}",
            "text": linkedin_post
        })
        print(f"LinkedIn email sent! ID: {r}")
    except Exception as e:
        print(f"LinkedIn email failed: {e}")


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

    # Generate and send LinkedIn post (Haiku — cheap)
    print("Generating LinkedIn post...")
    linkedin_post = generate_linkedin_post(today, brief)
    print(f"LinkedIn post:\n{linkedin_post[:300]}...")
    send_linkedin_email(today, linkedin_post)
    print("Done!")
