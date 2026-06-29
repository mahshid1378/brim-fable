"""real facts from the open web.

web_search is a server-side tool — fable issues a query, anthropic runs it,
and real results come back with citations. this is how a fact becomes real
instead of remembered: it came from outside the model, just now.
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]


def look_up(question: str) -> str:
    """ask the live web a question, get a grounded answer back."""
    response = client.messages.create(
        model="claude-fable-5",
        max_tokens=4000,
        thinking={"type": "adaptive"},
        tools=WEB_TOOLS,
        messages=[{"role": "user", "content": question}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()
