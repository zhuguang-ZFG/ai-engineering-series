"""Conservative report for one complete codex exec JSONL turn.

The fixture streams are authored examples, not recorded model executions.
Unknown events are retained as diagnostics and prevent automatic acceptance.
"""
import argparse
import json
from pathlib import Path


def inspect(lines, process_exit):
    thread_id = None
    started = 0
    terminal = None
    items = {}
    diagnostics = []
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON") from exc
        if not isinstance(event, dict):
            raise ValueError(f"line {line_no}: expected object")
        kind = event.get("type")
        if terminal is not None:
            diagnostics.append(f"line {line_no}: event after terminal")
        if kind == "thread.started":
            if thread_id is not None:
                diagnostics.append("duplicate thread.started")
            thread_id = event.get("thread_id")
        elif kind == "turn.started":
            started += 1
        elif kind in ("item.started", "item.updated", "item.completed"):
            item = event.get("item")
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError(f"line {line_no}: item.id is required")
            if kind != "item.completed" and item["id"] not in items and kind == "item.updated":
                diagnostics.append(f"update without start: {item['id']}")
            items[item["id"]] = {**item, "terminal": kind == "item.completed"}
        elif kind in ("turn.completed", "turn.failed"):
            terminal = kind
        elif kind == "error":
            diagnostics.append(event.get("message", "stream error"))
        else:
            diagnostics.append(f"unknown event: {kind}")
    unfinished = [key for key, item in items.items() if not item["terminal"]]
    failed_commands = [key for key, item in items.items()
                       if item.get("type") == "command_execution"
                       and (item.get("status") != "completed" or item.get("exit_code") != 0)]
    failed_items = [key for key, item in items.items()
                    if item.get("status") in ("failed", "declined")
                    or item.get("type") == "error"]
    stream_ok = (process_exit == 0 and bool(thread_id) and started == 1
                 and terminal == "turn.completed" and not unfinished and not diagnostics)
    return {"thread_id": thread_id, "turn_terminal": terminal,
            "process_exit": process_exit, "stream_ok": stream_ok,
            "failed_commands": failed_commands, "unfinished_items": unfinished,
            "failed_items": failed_items,
            "diagnostics": diagnostics,
            "needs_review": not stream_ok or bool(failed_commands or failed_items)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()
    try:
        report = inspect(args.events.read_text(encoding="utf-8").splitlines(), args.exit_code)
    except ValueError as exc:
        print(str(exc))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["needs_review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
