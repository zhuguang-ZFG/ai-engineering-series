"""Probe a real Kimi CLI's help and ACP handshake without a model request.

Run from the repository root. Every invocation uses a new temporary data root.
No login, session creation, import, or prompt request is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading


def probe(binary: str) -> dict:
    executable = Path(shutil.which(binary) or binary).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="kimi-book-probe-") as directory:
        root = Path(directory)
        workspace = root / "workspace"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        data = root / "data"
        data.mkdir()
        (data / "config.toml").write_text("telemetry = false\nauto_session_title = false\n",
                                         encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith("KIMI_")}
        env.update(KIMI_CODE_HOME=str(data), KIMI_DISABLE_TELEMETRY="1")
        def command(*args):
            return subprocess.run([str(executable), *args], cwd=workspace, env=env,
                                  text=True, encoding="utf-8", capture_output=True, timeout=20)
        version = command("--version")
        version.check_returncode()
        help_result = command("--help")
        help_result.check_returncode()
        export_help = command("export", "--help")
        export_help.check_returncode()
        acp = subprocess.Popen([str(executable), "acp"], cwd=workspace, env=env,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding="utf-8",
                               bufsize=1)
        messages: queue.Queue = queue.Queue()
        errors = []
        def read_stdout():
            for line in acp.stdout:
                try:
                    messages.put(json.loads(line))
                except ValueError:
                    messages.put({"unexpected_stdout": line.strip()})
        def read_stderr():
            for line in acp.stderr:
                errors.append(line)
        threads = [threading.Thread(target=read_stdout, daemon=True),
                   threading.Thread(target=read_stderr, daemon=True)]
        for thread in threads:
            thread.start()
        try:
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                    "protocolVersion": 1, "clientCapabilities": {},
                    "clientInfo": {"name": "kimi-book-probe", "version": "1.0.0"}}},
                {"jsonrpc": "2.0", "id": 2, "method": "book/unknown", "params": {}},
            ]
            responses = {}
            for request in requests:
                acp.stdin.write(json.dumps(request) + "\n")
                acp.stdin.flush()
                while request["id"] not in responses:
                    message = messages.get(timeout=25)
                    if "unexpected_stdout" in message:
                        raise RuntimeError("Non-JSON text appeared on the ACP channel")
                    if "id" in message:
                        responses[message["id"]] = message
            result = responses[1]["result"]
            assert result["agentInfo"]["version"] == version.stdout.strip(), result
            assert responses[2]["error"]["code"] == -32601, responses[2]
            # Auth metadata contains host paths; keep only public capability data.
            report = {"version": version.stdout.strip(),
                      "binary_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                      "help_options": {option: option in help_result.stdout for option in
                                       ("--agent-file", "--skills-dir", "--continue", "--plan",
                                        "--output-format", "import-sessions")},
                      "export_can_exclude_global_log": "--no-include-global-log" in export_help.stdout,
                      "acp": {"protocolVersion": result["protocolVersion"],
                              "agentInfo": result["agentInfo"],
                              "agentCapabilities": result["agentCapabilities"],
                              "unknown_method_error": responses[2]["error"]["code"]},
                      "model_requests": 0,
                      "scope": "real CLI help and ACP initialize only; no session/prompt or IDE tested"}
        finally:
            acp.terminate()
            try:
                acp.wait(timeout=10)
            except subprocess.TimeoutExpired:
                acp.kill()
                acp.wait(timeout=5)
            for thread in threads:
                thread.join(timeout=5)
            for stream in (acp.stdin, acp.stdout, acp.stderr):
                stream.close()
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", default="kimi")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = probe(args.binary)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
