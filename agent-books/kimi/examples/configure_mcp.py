"""Create project-local MCP configuration in an exercise copy; never overwrite."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
server = root / "review-plugin" / "rules_server.py"
config = root / ".kimi-code" / "mcp.json"
config.parent.mkdir(exist_ok=True)
with config.open("x", encoding="utf-8") as stream:
    json.dump({"mcpServers": {"chengming-rules": {
        "command": sys.executable, "args": [str(server)], "cwd": str(root)
    }}}, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(config)
