"""
Substack Newsletter Generator — "Today in Gen Z Finance"
Generates a copy-paste-ready Substack post with controversial
hot takes from a 24-year-old Gen Z male perspective.

Uses Claude + web search to find this week's stories,
then rewrites them with personality and opinions.

Posts as a GitHub Issue + emails to sharrank@budgetcaddie.com.
Runs daily via GitHub Actions (9 AM EST).
"""

import os
import subprocess
import time
from datetime import datetime, timezone, timedelta
import anthropic


def generate_substack_post():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    est = timezone(timedelta(hours=-4))
    today = datetime.now(est)
    date_str = today.strftime("%B %d, %Y")
    day_str = today.strftime("%A, %B %d")

    research_prompt = f"""Today is {date_str}. Search the web and find 5-7 money/finance news stories from today or yesterday that are relevant to young people (ages 18-28).

Look for stories across these categories:
- Cost of living changes (rent, groceries, gas, subscriptions)
- Stock market moves Gen Z cares about (Tesla, Nvidia, meme stocks, IPOs)
- Student loan or education cost news
- Job market shifts, layoffs, hiring trends
- Crypto and digital assets
- Government policy affecting young people (taxes, benefits, tariffs)
- Housing market and homeownership
- Side hustle economy and gig work
- BNPL, credit cards, fintech news
- Viral money stories or financial controversies
- Inflation, interest rates, recession signals
- Big tech moves that affect wallets

For each story provide:
1. The headline / what happened (with real numbers and facts)
2. The source URL
3. Why it matters to someone in their early 20s

Be specific with numbers, dates, and facts. No vague summaries."""

    # Step 1: Research stories with web search
    response = None
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=5000,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 15}],
                messages=[{"role": "user", "content": research_prompt}]
            )
            break
        except anthropic.APIStatusError as e:
            if e.status_code != 529:
                raise
            wait = 30 * (attempt + 1)
            print(f"API overloaded (attempt {attempt + 1}/5). Retrying in {wait}s...")
            time.sleep(wait)

    if response is None:
        raise Exception("Claude API overloaded after 5 retries.")

    # Extract research
    research = []
    for block in response.content:
        if hasattr(block, "text"):
            research.append(block.text)
    research_text = "\n".join(research)

    # Step 2: Rewrite as Substack newsletter with hot takes
    substack_prompt = f"""You are Sharran — a 24-year-old Gen Z guy who writes a daily Substack newsletter called "Today in Gen Z Finance". You break down money news for people your age who don't have time to read the Wall Street Journal but need to know what's happening to their wallet.

YOUR PERSONALITY — this is what makes people subscribe and share:
- You're the friend in the group chat who reads the news and makes everyone laugh while explaining it.
- Your humor is self-deprecating and painfully relatable. "Laugh at my pain" energy. You're broke, you know it, and you're funny about it. You joke about checking your bank account like it's a horror movie. You compare rent prices to your salary like it's a comedy bit. You're the guy who says "I'm never financially recovering from this" and means it literally.
- You make dark humor out of real financial pain. Not edgy for the sake of it — funny because it's TRUE and your generation lives it every day.
- You have STRONG opinions but you deliver them wrapped in jokes. The humor is the vehicle for the real point. People laugh, then go "wait... he's right though."
- You're frustrated about housing, wages, and the system — but you cope with humor instead of doom. Think stand-up comedian who happens to read the financial news.
- You roast companies, politicians, and bad advice the way you'd roast your friends. Specific, creative, never generic.
- You're pro building wealth young, pro investing, anti-dumb debt, skeptical of get-rich-quick nonsense.
- You keep it real about Gen Z too — you'll clown your own generation when they deserve it.

YOUR WRITING STYLE — this is critical for sounding human, not AI:
- Write like you actually talk. Sentence fragments are fine. Start sentences with "And" or "But". Trail off with "..."
- Mix up your sentence lengths constantly. A long one explaining something, then a short one for the punchline. "That's it. That's the story."
- Use specific personal details and hypothetical scenarios. "Me, a 24-year-old, staring at my Robinhood account like it owes me an apology." Not generic "young people are struggling."
- Reference real cultural touchpoints — Netflix shows, memes, TikTok trends, things Gen Z actually talks about.
- Your "My take" sections should each sound DIFFERENT from each other. Some should be funny rants. Some should be sarcastic one-liners. Some should be genuine frustration that lands hard. Some should be absurd comparisons. Vary the emotional tone across stories — do NOT use the same structure or energy for every single take.
- Never use the same phrases twice in one newsletter. No repeating "let that sink in" or "nobody's talking about this" or "here's the thing" across multiple stories. Each take needs its own flavor.
- NEVER use em dashes or en dashes (the long dash character). Use periods, commas, or just start a new sentence instead. Dashes are the #1 giveaway that AI wrote something.
- NEVER use fancy or uncommon words. No "jargon", "leverage", "nuanced", "landscape", "paradigm", "delve", "myriad", "robust", "tapestry", "realm", "foster", "utilize", "facilitate", "comprehensive", "moreover", "furthermore", "notably", "essentially", "inherently". Write like a normal 24 year old talks. If you wouldn't say it out loud to your friend, don't write it.
- Avoid AI-sounding patterns: no "In a world where...", no "It's worth noting that...", no "The reality is...", no "At the end of the day...", no "Here's the thing...", no "Let's break this down...". If it sounds like a LinkedIn post from a 45-year-old, delete it.
- Use callbacks and running jokes within the newsletter — reference an earlier story later, tie things together like a real person would.

IMPORTANT RULES:
- Every fact and number MUST come from the research below. Do NOT make up statistics.
- Be genuinely opinionated. Don't hedge. Don't "both sides" everything. Have a take.
- Swear sparingly for emphasis (damn, BS, hell) but don't overdo it.
- No emojis anywhere.
- Write headlines that make people NEED to click. Curiosity gaps, bold claims, "nobody's talking about this" energy.
- Write in a way that makes people want to screenshot, share, and argue in the comments.
- The goal is ENGAGEMENT — every section should make the reader feel something. But vary WHAT they feel — one story makes them laugh, the next one pisses them off, the next one makes them go "oh damn I didn't know that."
- VARIETY IS EVERYTHING. If every "My take" sounds the same, you failed. Each one needs a different comedic or emotional angle.

Here are the stories I researched today:
{research_text}

Now write the full Substack newsletter. Use this EXACT structure:

---

# [CLICKABLE TITLE — rotate between styles like these. Be creative. Make it impossible to scroll past:]
# Examples (pick ONE style, don't copy these exactly):
# "5 money stories you missed this week that are quietly screwing Gen Z"
# "Nobody's talking about what just happened to your rent"
# "The money news they don't want 24-year-olds to see"
# "Your paycheck just got worse and here's why"
# "What you missed in Gen Z finance while you were doomscrolling"
# "I read the financial news so you don't have to. You should be pissed."

**{day_str}. The money news you were too busy to catch, explained by someone who gives a damn.**

[Write a 2-4 sentence intro. Hook them IMMEDIATELY with the most shocking or relatable story of the day. Make them feel like they NEED to keep reading. Set the tone — fired up, a little provocative, like a voice note to your group chat.]

---

## 1. [Punchy, curiosity-driven headline — make them need to read the next line]

[3-5 sentences explaining what happened. Dead simple language. Real numbers. Paint the picture so a 22-year-old scrolling on their phone gets it instantly.]

**My take:** [Pick ONE approach — a self-deprecating joke about how this affects you personally, a sarcastic rant, a funny hypothetical, an absurd comparison, or a genuinely angry moment. DO NOT default to the same tone as the other takes.]

---

## 2. [Different energy headline — if story 1 was a question, make this one a bold statement. Mix it up.]

[Same explainer format but vary your analogies and references. Don't explain every story the same way.]

**My take:** [MUST be a different vibe than story 1's take. If you ranted above, be funny here. If you joked above, get real here.]

---

[Continue for all 5-7 stories. Each "My take" must use a DIFFERENT comedic or emotional approach. Rotate between: self-deprecating humor, sarcastic roasts, genuine anger, absurd comparisons, dark comedy, rhetorical questions that hit hard, personal anecdotes/scenarios. Never repeat the same approach twice in one newsletter.]

---

## The Bottom Line

[2-3 sentences wrapping up the day. What should a young person actually DO with this info? End with a line that sticks in their head and makes them come back tomorrow.]

---

*If you made it this far, you officially know more about money than 90% of people your age. Subscribe so you don't miss tomorrow's edition. Share it with that friend who still thinks a savings account is an investment strategy.*

*Download Budget Caddie on the App Store. Proactive AI that budgets, tracks, and coaches you before you overspend.*

---

OUTPUT ONLY THE NEWSLETTER. No preamble, no "here's the post", nothing outside the newsletter itself."""

    substack_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=5000,
        messages=[{"role": "user", "content": substack_prompt}]
    )

    newsletter = substack_response.content[0].text.strip()
    return date_str, newsletter


def post_issue(date_str, newsletter):
    """Post the newsletter as a GitHub Issue."""
    title = f"Substack Draft — Today in Gen Z Finance — {date_str}"

    with open("/tmp/substack_body.md", "w") as f:
        f.write("# Copy-paste this into Substack\n\n")
        f.write(newsletter)

    subprocess.run([
        "gh", "issue", "create",
        "--repo", os.environ.get("GITHUB_REPOSITORY", "Sharranrae/daily-money-brief"),
        "--title", title,
        "--body-file", "/tmp/substack_body.md",
        "--label", "substack-draft"
    ], check=True)


def send_email(date_str, newsletter):
    """Send the newsletter draft via Resend."""
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
            "subject": f"Substack Draft — {date_str}",
            "text": f"Your Substack newsletter is ready. Copy and paste into Substack:\n\n{newsletter}"
        })
        print(f"Email sent! ID: {r}")
    except Exception as e:
        print(f"Email failed: {e}")


if __name__ == "__main__":
    # Create label if it doesn't exist
    try:
        subprocess.run([
            "gh", "label", "create", "substack-draft",
            "--repo", os.environ.get("GITHUB_REPOSITORY", "Sharranrae/daily-money-brief"),
            "--color", "7B61FF",
            "--description", "Daily Substack newsletter draft"
        ], capture_output=True)
    except Exception:
        pass

    print("Generating your Substack post...\n")
    date_str, newsletter = generate_substack_post()

    print(newsletter[:500] + "...")

    post_issue(date_str, newsletter)
    print("Posted as GitHub Issue!")

    send_email(date_str, newsletter)
    print("Done!")
