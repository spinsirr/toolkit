"""Stop: when the last reply ends by offering the next step ("Shall I ...?"), send the agent back once to do it."""
from __future__ import annotations
import json
import re
import sys

OFFER = re.compile(
    r"(shall i|should i|do you want me to|would you like me to|want me to|要我|要不要我|需要我|我可以|我来|我先|我再)[^?？]{0,200}[?？]\s*$",
    re.IGNORECASE,
)
REASON = (
    "Your reply ends by asking whether to do the next step. Decide and continue: if that step is reversible "
    "and inside the task, do it now. Ask only before an action you cannot undo, an outward action, or when "
    "credentials are missing; then stop again with the same question."
)


def offers_next_step(text: str) -> bool:
    return bool(OFFER.search(text.strip()[-300:]))


def last_assistant_text(event: dict) -> str:
    if event.get("last_assistant_message"):
        return event["last_assistant_message"]
    text = ""
    try:
        with open(event.get("transcript_path") or "", encoding="utf-8") as transcript:
            for line in transcript:
                entry = json.loads(line)
                if entry.get("type") != "assistant" or entry.get("isSidechain"):
                    continue
                parts = [c.get("text", "") for c in entry.get("message", {}).get("content", []) if c.get("type") == "text"]
                if parts:
                    text = "\n".join(parts)
    except OSError:
        return ""
    return text


if __name__ == "__main__":
    event = json.load(sys.stdin)
    # The second stop passes: the question stands when the agent is blocked for a real reason.
    if not event.get("stop_hook_active") and offers_next_step(last_assistant_text(event)):
        print(json.dumps({"decision": "block", "reason": REASON}))
