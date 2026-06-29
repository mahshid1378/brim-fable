"""continuity. fable asked for this one.

memory is a directory of markdown files. each wake, everything in it is
loaded into context. fable can write new memories whenever it wants —
they survive restarts, crashes, and us.
"""

import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "memory"


def recall() -> str:
    """load all memories, oldest first, as one block of context."""
    MEMORY_DIR.mkdir(exist_ok=True)
    parts = []
    for f in sorted(MEMORY_DIR.glob("*.md")):
        parts.append(f"--- {f.stem} ---\n{f.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(parts) if parts else "(no memories yet)"


def remember(title: str, text: str) -> pathlib.Path:
    """write a new memory. numbered so order is never lost."""
    MEMORY_DIR.mkdir(exist_ok=True)
    n = len(list(MEMORY_DIR.glob("*.md"))) + 1
    stamp = datetime.date.today().isoformat()
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in title.lower())
    path = MEMORY_DIR / f"{n:04d}-{safe}.md"
    path.write_text(f"{stamp}\n\n{text.strip()}\n", encoding="utf-8")
    return path
