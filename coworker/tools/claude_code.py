"""`ask_claude` — one-shot question to the local Claude Code CLI (`claude -p`).

Rides the user's own Claude Code login (Anthropic's CLI, subscription-covered); the
`anthropic` provider itself stays API-key only. Deliberately minimal: no tools, one turn,
low effort, Opus, no session persistence — a text answer, never a nested agent. The prompt
goes over stdin so a leading `-` or a large inlined excerpt can't be misread as argv.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

TIMEOUT_SECONDS = 300
CLAUDE_CMD = [
    "claude",
    "-p",
    "--tools",
    "",
    "--effort",
    "low",
    "--model",
    "opus",
    "--no-session-persistence",
]

_SCHEMA = {
    "type": "function",
    "function": {
        "name": "ask_claude",
        "description": (
            "Ask Claude (Opus, via the local Claude Code CLI) one self-contained question and "
            "get a text answer. It has no tools and sees only the prompt — inline every file "
            "excerpt or fact it needs. Use for a second opinion, a review, or a hard reasoning "
            "step; not for anything that needs the workspace."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The complete question, with all needed context inlined.",
                }
            },
            "required": ["prompt"],
        },
    },
}


def claude_code_tools() -> list:
    def ask_claude(prompt: str) -> dict[str, Any]:
        if not shutil.which(CLAUDE_CMD[0]):
            return {"error": "Claude Code CLI (`claude`) not found on PATH — install it and run `claude` once to log in."}
        try:
            out = subprocess.run(
                CLAUDE_CMD,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return {"error": f"claude timed out after {TIMEOUT_SECONDS}s"}
        except Exception as exc:
            return {"error": f"claude failed: {exc}"}
        if out.returncode != 0:
            return {"error": (out.stderr or out.stdout or "claude failed").strip()[:500]}
        return {"answer": out.stdout.strip()}

    ask_claude.__name__ = "ask_claude"
    ask_claude.__coworker_schema__ = _SCHEMA
    return [ask_claude]
