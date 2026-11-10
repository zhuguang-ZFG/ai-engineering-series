"""Minimal read-only MCP stdio example; no filesystem or network access."""
from __future__ import annotations

import json
import sys

RULES = {
    "quantity": "quantity must be a positive integer; bool is not accepted",
    "stock": "stock must be a non-negative integer; bool is not accepted",
    "boundary": "quantity equal to stock is valid and leaves zero stock",
}


def handle(request: dict) -> dict | None:
    if "id" not in request:
        return None
    method = request.get("method")
    result = None
    if method == "initialize":
        result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "chengming-rules", "version": "1.0.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": "get_rule", "description": "Read an inventory rule",
                            "inputSchema": {"type": "object", "properties": {
                                "rule": {"type": "string", "enum": list(RULES)}},
                                "required": ["rule"], "additionalProperties": False}}]}
    elif method == "tools/call":
        params = request.get("params", {})
        args = params.get("arguments", {}) if isinstance(params, dict) else {}
        valid = (isinstance(params, dict) and params.get("name") == "get_rule"
                 and isinstance(args, dict) and set(args) == {"rule"}
                 and isinstance(args.get("rule"), str) and args["rule"] in RULES)
        result = {"content": [{"type": "text", "text": RULES[args["rule"]] if valid
                               else "Unknown tool or invalid rule arguments"}], "isError": not valid}
    if result is None:
        return {"jsonrpc": "2.0", "id": request["id"], "error": {
            "code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": request["id"], "result": result}


if __name__ == "__main__":
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("expected an object")
            response = handle(request)
        except (ValueError, TypeError):
            response = {"jsonrpc": "2.0", "id": None, "error": {
                "code": -32700, "message": "Invalid JSON-RPC input"}}
        if response is not None:
            print(json.dumps(response), flush=True)
