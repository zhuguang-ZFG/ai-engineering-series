"""Teaching hook: reject three named write/command tools during a review."""
from __future__ import annotations

import json
import sys


def decision(payload: dict) -> dict:
    if (payload.get("hook_event_name") == "PreToolUse"
            and payload.get("tool_name") in {"Write", "Edit", "Bash"}):
        return {"hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": "This review only reads files; start a separate repair task."
        }}
    return {}


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("hook payload must be an object")
        print(json.dumps(decision(payload)))
    except (ValueError, TypeError) as error:
        print(f"invalid hook input: {error}", file=sys.stderr)
        raise SystemExit(1)
