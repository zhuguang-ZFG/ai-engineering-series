"""Exercise OpenCode 1.19.5 V1 plugins through the real local HTTP host.

Requires a separately downloaded CLI and preinstalled plugin dependencies.
Only the model protocol is simulated. No real credentials are inherited.
Run from the book repository; see README.md for setup and limits.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request

VERSION = "1.19.5"
COMMIT = "810c0eba1a7348036f8bdf61e6632d0c36c6876c"
HIDDEN = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
REPO = Path(__file__).resolve().parents[2]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def isolated_env(root: Path) -> dict[str, str]:
    # Retain executable lookup and Windows runtime essentials, not provider,
    # proxy, account, OPENCODE_* or user configuration environment variables.
    keep = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT",
            "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE",
            "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA"}
    env = {k: v for k, v in os.environ.items() if k.upper() in keep}
    env.update({
        "OPENCODE_TEST_HOME": str(root / "home"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_STATE_HOME": str(root / "state"),
        "OPENCODE_DB": str(root / "state/opencode.db"),
        "TEMP": str(root / "tmp"), "TMP": str(root / "tmp"),
        "TMPDIR": str(root / "tmp"),
        "OPENCODE_CONFIG_CONTENT": "{}",
        "OPENCODE_DISABLE_MODELS_FETCH": "true",
        "OPENCODE_DISABLE_AUTOUPDATE": "true",
        "OPENCODE_DISABLE_DEFAULT_PLUGINS": "true",
        "OPENCODE_DISABLE_EXTERNAL_SKILLS": "true",
        "OPENCODE_DISABLE_CLAUDE_CODE": "true",
        "OPENCODE_DISABLE_LSP_DOWNLOAD": "true",
        "OPENCODE_DISABLE_FFF": "true",
        "OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER": "true",
        "OPENCODE_SERVER_PASSWORD": secrets.token_hex(16),
    })
    return env


def seed_dependencies(source: Path, target: Path) -> None:
    # Copy real, already-installed files; do not stub npm metadata or weaken
    # the host's dependency checks. These copies remain inside the fixture.
    target.mkdir(parents=True, exist_ok=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copy2(source / name, target / name)
    shutil.copytree(source / "node_modules", target / "node_modules")


def write_plugins(project: Path, trace: Path) -> Path:
    directory = project / ".opencode/plugins"
    directory.mkdir()
    shutil.copy2(Path(__file__).with_name("review-trace.ts"),
                 project / ".opencode/review-trace.ts")
    recorder = (
        'import { appendFileSync } from "node:fs";\n'
        f"const file = {json.dumps(str(trace))};\n"
        'const record = (event, data = {}) => appendFileSync(file, '
        'JSON.stringify({plugin: NAME,event,...data})+"\\n");\n'
    )
    wrapper = recorder.replace("NAME", '"A"') + """
import { ReviewTrace } from "../review-trace.ts";
let generation = 0;
export const Probe = async (ctx) => {
  const current = ++generation;
  const inner = await ReviewTrace(ctx);
  record("init", {generation: current});
  return {
    config: async () => record("config"),
    "experimental.chat.system.transform": async (input, output) => {
      await inner["experimental.chat.system.transform"](input, output);
      output.system.push("BOOK_PLUGIN_A");
      record("system");
    },
    "tool.execute.before": async (input, output) => {
      record("before", {tool:input.tool,callID:input.callID});
      await inner["tool.execute.before"](input, output);
    },
    "tool.execute.after": async (input, output) => {
      await inner["tool.execute.after"](input, output);
      record("after", {tool:input.tool,callID:input.callID,
                      trace:output?.metadata?.reviewTrace});
    },
    dispose: async () => { await inner.dispose(); record("dispose"); }
  };
};
"""
    path = directory / "a.ts"
    path.write_text(wrapper, encoding="utf-8")
    (project / "b.ts").write_text(recorder.replace("NAME", '"B"') + """
export default async () => {
  record("init");
  return {
    config: async () => record("config"),
    "experimental.chat.system.transform": async (_i, o) => {
      o.system.push("BOOK_PLUGIN_B"); record("system");
    },
    "tool.execute.before": async () => record("before"),
    "tool.execute.after": async () => record("after"),
    dispose: async () => record("dispose")
  };
};
""", encoding="utf-8")
    return path


class ModelFixture(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length < 4_000_000 or len(self.server.requests) >= 24:
            self.send_error(400, "fixture request limit")
            return
        payload = json.loads(self.rfile.read(length))
        self.server.requests.append(payload)
        tools = {t["function"]["name"] for t in payload.get("tools", []) if "function" in t}
        has_result = any(m.get("role") == "tool" for m in payload.get("messages", []))
        call_tool = "read" in tools and not has_result
        chunks = [{"role": "assistant"}]
        if call_tool:
            chunks.append({"tool_calls": [{
                "index": 0, "id": "call_book_read", "type": "function",
                "function": {"name": "read", "arguments": json.dumps({
                    "filePath": str(self.server.fixture),
                })},
            }]})
        else:
            chunks.append({"content": "BOOK_FIXTURE_DONE"})
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        for delta in chunks:
            self.emit(delta, None)
        self.emit({}, "tool_calls" if call_tool else "stop")
        self.wfile.write(b"data: [DONE]\n\n")

    def emit(self, delta: dict, finish: str | None) -> None:
        data = {
            "id": "chatcmpl-book", "object": "chat.completion.chunk",
            "created": 1, "model": "fixture",
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }
        if finish:
            data["usage"] = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        self.wfile.write(("data: " + json.dumps(data) + "\n\n").encode())


class Host:
    def __init__(self, binary: Path, project: Path, env: dict, root: Path,
                 name: str, pure: bool = False):
        # Reserve a candidate ephemeral port; if another process wins the
        # short handoff race, startup must fail rather than contact that host.
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.base = f"http://127.0.0.1:{port}"
        self.project = project
        self.auth = base64.b64encode(
            ("opencode:" + env["OPENCODE_SERVER_PASSWORD"]).encode()).decode()
        self.log_path = root / f"{name}.log"
        self.log = self.log_path.open("w", encoding="utf-8")
        command = [str(binary), "serve", "--hostname", "127.0.0.1",
                   "--port", str(port), "--print-logs"]
        if pure:
            command.append("--pure")
        try:
            self.proc = subprocess.Popen(command, cwd=project, env=env, stdout=self.log,
                                         stderr=subprocess.STDOUT, creationflags=HIDDEN)
        except BaseException:
            self.log.close()
            raise
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                text = self.log_path.read_text(encoding="utf-8", errors="replace")
                if f"listening on {self.base}" in text:
                    break
                if self.proc.poll() is not None:
                    raise RuntimeError(f"Host exited; see {self.log_path}")
                time.sleep(0.1)
            else:
                raise TimeoutError(f"Host startup; see {self.log_path}")
        except BaseException:
            self.close()
            raise

    def request(self, method: str, path: str, body: dict | None = None):
        headers = {"Authorization": "Basic " + self.auth,
                   "x-opencode-directory": str(self.project)}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.base + path, method=method, headers=headers,
            data=json.dumps(body).encode() if body is not None else None)
        # Ignore proxy environment from the process running this driver too.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=45) as response:
            return json.load(response)

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        self.log.close()


def events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def exercise(host: Host, model, trace: Path, name: str, expected_marker: str | None,
             generation: int | None) -> dict:
    start = len(events(trace))
    request_start = len(model.requests)
    session = host.request("POST", "/session", {})
    answer = host.request("POST", f"/session/{session['id']}/message", {
        "model": {"providerID": "fixture", "modelID": "test"},
        "parts": [{"type": "text", "text": "Read fixture.txt and report the fixture marker."}],
    })
    assert not answer["info"].get("error"), answer["info"].get("error")
    assert any(p.get("text") == "BOOK_FIXTURE_DONE" for p in answer["parts"])
    calls = model.requests[request_start:]
    assert any(m.get("role") == "tool" and "BOOK_FIXTURE_ALPHA" in str(m.get("content"))
               for call in calls for m in call.get("messages", [])), "real read result missing"
    systems = ["\n".join(str(m["content"]) for m in call.get("messages", [])
                         if m.get("role") == "system") for call in calls]
    assert host.request("POST", "/instance/dispose") is True
    if expected_marker:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if len([e for e in events(trace)[start:] if e["event"] == "dispose"]) == 2:
                break
            time.sleep(0.05)
        seen = events(trace)[start:]
        for event in ("init", "config", "before", "after", "dispose"):
            assert [e["plugin"] for e in seen if e["event"] == event] == ["B", "A"], (event, seen)
        assert [e["generation"] for e in seen if e["plugin"] == "A" and e["event"] == "init"] == [generation]
        after = next(e for e in seen if e["plugin"] == "A" and e["event"] == "after")
        assert after["trace"]["correlated"] and after["trace"]["durationMs"] >= 0
        assert systems and all("BOOK_PLUGIN_B" in s and expected_marker in s for s in systems)
        assert all(s.index("BOOK_PLUGIN_B") < s.index(expected_marker) for s in systems)
    else:
        seen = events(trace)[start:]
        assert not seen, seen
        assert systems and all("BOOK_PLUGIN_" not in s for s in systems)
    return {"case": name, "passed": True, "model_requests": len(calls),
            "hook_events": [f"{e['plugin']}:{e['event']}" for e in seen]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--dependency-dir", type=Path, required=True)
    args = parser.parse_args()
    binary, dependency = args.binary.resolve(strict=True), args.dependency_dir.resolve(strict=True)
    installed = json.loads((dependency / "node_modules/@opencode-ai/plugin/package.json").read_text())
    assert installed["version"] == VERSION, "plugin dependency version mismatch"
    output = REPO / ".scratch/agent-series"
    output.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="host-plugins-", dir=output))
    for folder in ("home", "config", "data", "cache", "state", "tmp", "project"):
        (root / folder).mkdir()
    env = isolated_env(root)
    project = root / "project"
    version = subprocess.run([str(binary), "--version"], cwd=project, env=env,
                             capture_output=True, text=True, timeout=30,
                             check=True, creationflags=HIDDEN).stdout.strip()
    assert version == VERSION, f"Expected {VERSION}; got {version}"
    paths = subprocess.run([str(binary), "debug", "paths"], cwd=project, env=env,
                           capture_output=True, text=True, timeout=30,
                           check=True, creationflags=HIDDEN).stdout
    path_names = set()
    for line in paths.splitlines():
        if line.strip():
            name, directory = line.split(maxsplit=1)
            path_names.add(name)
            assert Path(directory).resolve().is_relative_to(root), line
    assert {"home", "data", "config", "cache", "state", "tmp"} <= path_names
    subprocess.run(["git", "-c", "init.templateDir=", "init", "-q", str(project)],
                   check=True, capture_output=True, env=env, creationflags=HIDDEN)
    for directory in (root / "config/opencode", project / ".opencode"):
        seed_dependencies(dependency, directory)
    trace = root / "events.jsonl"
    wrapper = write_plugins(project, trace)
    fixture = project / "fixture.txt"
    fixture.write_text("BOOK_FIXTURE_ALPHA\n", encoding="utf-8")
    model = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ModelFixture)
    model.requests, model.fixture = [], fixture
    thread = threading.Thread(target=model.serve_forever, daemon=True)
    thread.start()
    write_json(project / "opencode.json", {
        "plugin": ["./b.ts"], "model": "fixture/test", "small_model": "fixture/test",
        "enabled_providers": ["fixture"], "share": "disabled", "snapshot": False,
        "autoupdate": False, "permission": {"*": "deny", "read": "allow"},
        "provider": {"fixture": {"npm": "@ai-sdk/openai-compatible", "name": "Fixture",
            "options": {"baseURL": f"http://127.0.0.1:{model.server_port}/v1",
                        "apiKey": "local-fixture-only"},
            "models": {"test": {"name": "test", "limit": {"context": 32000, "output": 1024}}}}},
    })
    report = {"version": version, "source_commit": COMMIT, "platform": os.name,
              "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
              "external_model_used": False, "filesystem_watch_disabled": True, "cases": []}
    host = None
    try:
        host = Host(binary, project, env, root, "initial")
        report["cases"].append(exercise(host, model, trace, "discovery-and-real-read", "BOOK_PLUGIN_A", 1))
        assert "Tool result observed" in host.log_path.read_text(encoding="utf-8")
        report["real_sdk_log_observed"] = True
        print("PASS discovery, real read, ordered hooks and disposal", flush=True)
        wrapper.write_text(wrapper.read_text(encoding="utf-8").replace(
            "BOOK_PLUGIN_A", "BOOK_PLUGIN_A_EDITED"), encoding="utf-8")
        broken = project / ".opencode/plugins/broken.ts"
        broken.write_text(
            'import {appendFileSync} from "node:fs";\n'
            'export default async () => { appendFileSync(' + json.dumps(str(trace)) +
            ', JSON.stringify({plugin:"broken",event:"failed-init"})+"\\n");'
            ' throw new Error("BOOK_FIXTURE_INIT_ERROR"); };\n', encoding="utf-8")
        report["cases"].append(exercise(host, model, trace, "same-process-reinitialization", "BOOK_PLUGIN_A", 2))
        # Check the exact old token; substring inclusion alone would also
        # accept BOOK_PLUGIN_A_EDITED.
        assert all("BOOK_PLUGIN_A_EDITED" not in json.dumps(r) for r in model.requests)
        assert any(e["event"] == "failed-init" for e in events(trace))
        print("PASS failed plugin isolation and cached module after reinitialization", flush=True)
        host.close()
        host = Host(binary, project, env, root, "restart")
        report["cases"].append(exercise(host, model, trace, "new-process-reloads-module", "BOOK_PLUGIN_A_EDITED", 1))
        print("PASS new process observes edited source", flush=True)
        host.close()
        host = Host(binary, project, env, root, "pure", pure=True)
        report["cases"].append(exercise(host, model, trace, "pure-skips-external-plugins", None, None))
        print("PASS --pure skips external plugins", flush=True)
        assert fixture.read_text(encoding="utf-8") == "BOOK_FIXTURE_ALPHA\n"
        report["fixture_unchanged"] = True
        report["passed"] = True
    finally:
        if host:
            host.close()
        model.shutdown()
        model.server_close()
        thread.join(timeout=5)
        write_json(root / "model-requests.json", model.requests)
        write_json(root / "report.json", report)
        print("Evidence:", root, flush=True)
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
