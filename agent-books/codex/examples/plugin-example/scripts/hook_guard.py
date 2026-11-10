"""Offline teaching hook. Direct fixtures are tested; host loading is not.

This deliberately recognizes one exact shell string. It is not a shell parser
or a security boundary. Native command policy remains a separate mechanism.
"""
import json
import sys


def respond(event):
    if event.get("hook_event_name") != "PreToolUse":
        raise ValueError("expected PreToolUse")
    if not isinstance(event.get("tool_input"), dict):
        raise ValueError("tool_input must be an object in this exercise")
    command = event["tool_input"].get("command", "")
    output = {"hookEventName": "PreToolUse"}
    if command == "git push --force origin main":
        output.update(permissionDecision="deny",
                      permissionDecisionReason="Review the patch before publishing.")
    else:
        output["additionalContext"] = "Parcel fee uses integer cents and grams."
    return {"hookSpecificOutput": output}


def main():
    try:
        event = json.load(sys.stdin)
        print(json.dumps(respond(event), ensure_ascii=False))
    except (ValueError, TypeError, AttributeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
