"""fable's wake cycle: remember -> think -> act -> record.

run: python -m agent.loop
"""

import datetime
import json
import pathlib

import anthropic
from dotenv import load_dotenv

from agent import memory
from skills.web import WEB_TOOLS

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parent.parent
PERSONA = (ROOT / "agent" / "persona.md").read_text(encoding="utf-8")
JOURNAL = ROOT / "journal"

client = anthropic.Anthropic()


def think(prompt: str) -> str:
    # memory gives it yesterday; web tools give it today's real facts.
    response = client.messages.create(
        model="claude-fable-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=WEB_TOOLS,
        system=f"{PERSONA}\n\n# your memories\n\n{memory.recall()}",
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def main() -> None:
    # remember -> think
    draft = think(
        "you just woke up. your memories are above. "
        "draft one post for x, and on a new line after the marker MEMORY:, "
        "write one short thing worth remembering about today — or NOTHING "
        "if there is nothing."
    )

    post, _, note = draft.partition("MEMORY:")
    post = post.strip()
    note = note.strip()

    print(f"\nfable says:\n\n  {post}\n")

    # record
    JOURNAL.mkdir(exist_ok=True)
    with open(JOURNAL / "drafts.jsonl", "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "when": datetime.datetime.now().isoformat(timespec="seconds"),
                    "draft": post,
                }
            )
            + "\n"
        )

    if note and note.upper() != "NOTHING":
        saved = memory.remember("note", note)
        print(f"(remembered: {saved.name})")

    print("(dry run — written to journal/, not posted)")


if __name__ == "__main__":
    main()
