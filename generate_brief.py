"""
Daily Gen Z Money Brief Generator
Uses Claude API with web search to find today's top finance stories.
Posts the result as a GitHub Issue.
"""

import os
import json
import subprocess
from datetime import datetime, timezone, timedelta
import anthropic

def generate_brief():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    est = timezone(timedelta(hours=-4))
    today = datetime.now(est).strftime("%B %d, %Y")

    prompt = f"""Today is {today}. Find the top 5 money and finance news stories from today or this week that impact young people (ages 18-28).

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

1. HEADLINE — one punchy line (TikTok hook)
2. WHAT HAPPENED — 2-3 sentences. Explain it like you're telling a 6th grader. No jargon. Simple words.
3. WHY YOU SHOULD CARE — 1-2 sentences connecting it to a young person's wallet. Make it feel personal.
4. TIKTOK ANGLE — The opening line I'd say to camera and the vibe (funny, shocking, educational, rant, storytime).

Format it clean. Number each story 1-5.

End with:
BONUS: One "did you know?" money fact I can use as a quick 15-second TikTok."""

    # Use Claude with web search enabled
    response = client.messages.create(
        model="claude-sonnet-4-6-20250514",
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
    title = f"Daily Money Brief — {today}"

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
