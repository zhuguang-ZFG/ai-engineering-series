"""Run custom-tool permission checks in the pinned official OpenCode host.

Only the model protocol is simulated. See README.md for isolated setup.
Do not run Python with -O: assertions are the experiment's checks.
"""
import argparse
import concurrent.futures
import hashlib
import shutil
import importlib.util
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid

EXAMPLES = Path(__file__).resolve().parent
REPO = EXAMPLES.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--binary", type=Path, required=True)
parser.add_argument("--dependency-dir", type=Path, required=True)
args = parser.parse_args()
spec = importlib.util.spec_from_file_location("host_plugins", EXAMPLES / "check-host-plugins.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
root = REPO / ".scratch/agent-series" / ("permissions-" + uuid.uuid4().hex[:10])
root = root.resolve()
root.mkdir(parents=True)
for name in ("home", "config", "data", "cache", "state", "tmp", "project"):
    (root / name).mkdir()
env = support.isolated_env(root)
project = root / "project"
binary = args.binary.resolve(strict=True)
dependency = args.dependency_dir.resolve(strict=True)
version = subprocess.run([str(binary), "--version"], cwd=project, env=env,
                         capture_output=True, text=True, timeout=30, check=True,
                         creationflags=support.HIDDEN).stdout.strip()
assert version == support.VERSION, version
installed = json.loads((dependency / "node_modules/@opencode-ai/plugin/package.json").read_text(encoding="utf-8"))
assert installed["version"] == support.VERSION
subprocess.run(["git", "-c", "init.templateDir=", "init", "-q", str(project)],
               check=True, env=env, creationflags=support.HIDDEN)
for directory in (root / "config/opencode", project / ".opencode"):
    support.seed_dependencies(dependency, directory)
trace = root / "events.jsonl"
fixture = project / "fixture.txt"
fixture.write_text("BOOK_PERMISSION_ALPHA\n", encoding="utf-8")
plugins = project / ".opencode/plugins"
plugins.mkdir()
shutil.copy2(EXAMPLES / "read-fixture.ts", project / ".opencode/read-fixture.ts")
(plugins / "probe.ts").write_text('''
import {appendFileSync} from "node:fs";
import {ReadFixture} from "../read-fixture.ts";
const trace = TRACE;
const record = (event) => appendFileSync(trace, JSON.stringify({event})+"\\n");
export default async (ctx) => {
  const hooks = await ReadFixture(ctx);
  const original = hooks.tool.book_probe.execute;
  hooks.tool.book_probe.execute = async (args, toolCtx) => {
    record("entered");
    const result = await original(args, {...toolCtx, ask: async (request) => {
      await toolCtx.ask(request); record("approved");
    }});
    record("read-done");
    return result;
  };
  return hooks;
};
'''.replace("TRACE", json.dumps(str(trace))), encoding="utf-8")


class Model(support.ModelFixture):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size < 4_000_000 or len(self.server.requests) >= 40:
            self.send_error(400)
            return
        payload = json.loads(self.rfile.read(size))
        self.server.requests.append(payload)
        names = {t["function"]["name"] for t in payload.get("tools", []) if "function" in t}
        result = any(m.get("role") == "tool" for m in payload.get("messages", []))
        invoke = "book_probe" in names and not result
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        self.emit({"role": "assistant"}, None)
        if invoke:
            self.emit({"tool_calls": [{"index": 0, "id": "call_permission_probe", "type": "function",
                       "function": {"name": "book_probe", "arguments": "{}"}}]}, None)
        else:
            self.emit({"content": "BOOK_PERMISSION_DONE"}, None)
        self.emit({}, "tool_calls" if invoke else "stop")
        self.wfile.write(b"data: [DONE]\n\n")


model = support.http.server.ThreadingHTTPServer(("127.0.0.1", 0), Model)
model.requests = []
thread = threading.Thread(target=model.serve_forever, daemon=True)
thread.start()
base = {
    "plugin": ["./.opencode/plugins/probe.ts"],
    "model": "fixture/test", "small_model": "fixture/test", "enabled_providers": ["fixture"],
    "share": "disabled", "snapshot": False, "autoupdate": False,
    "provider": {"fixture": {"npm": "@ai-sdk/openai-compatible", "name": "Fixture",
        "options": {"baseURL": f"http://127.0.0.1:{model.server_port}/v1", "apiKey": "local-fixture-only"},
        "models": {"test": {"name": "test", "limit": {"context": 32000, "output": 1024}}}}},
}
host = None
results = []
try:
    scenarios = (
        ("allow", "allow", None, True), ("deny", "deny", None, True),
        ("ask-once", "ask", "once", True), ("ask-reject", "ask", "reject", True),
        ("hidden", "allow", None, True),
        ("once-first", "ask", "once", False),
        ("once-new-session", "ask", "once", True),
        ("always-first", "ask", "always", False),
        ("always-new-session", "ask", None, True),
        ("always-after-dispose", "ask", "once", True),
    )
    for name, action, reply, reset_after in scenarios:
        config = dict(base, permission={"*": "deny", "book_probe": "deny" if name == "hidden" else "allow", "book_read": action})
        support.write_json(project / "opencode.json", config)
        if host is None:
            host = support.Host(binary, project, env, root, "permissions")
        first_event, first_request = len(support.events(trace)), len(model.requests)
        session = host.request("POST", "/session", {})
        prompt = {"model": {"providerID": "fixture", "modelID": "test"},
                  "parts": [{"type": "text", "text": "Use book_probe to read the fixed fixture."}]}
        asked = False
        if reply:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pending = pool.submit(host.request, "POST", f"/session/{session['id']}/message", prompt)
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    requests = host.request("GET", "/permission")
                    if requests:
                        request = next(r for r in requests if r["sessionID"] == session["id"])
                        assert request["permission"] == "book_read"
                        assert [e["event"] for e in support.events(trace)[first_event:]] == ["entered"]
                        host.request("POST", f"/permission/{request['id']}/reply", {"reply": reply})
                        asked = True
                        break
                    if pending.done():
                        raise AssertionError("message completed without expected permission request")
                    time.sleep(0.1)
                if not asked:
                    host.close()
                    raise TimeoutError("permission prompt missing")
                answer = pending.result(timeout=45)
        else:
            answer = host.request("POST", f"/session/{session['id']}/message", prompt)
        assert not answer["info"].get("error"), answer["info"]
        events = [e["event"] for e in support.events(trace)[first_event:]]
        calls = model.requests[first_request:]
        observed = any(m.get("role") == "tool" and "BOOK_PERMISSION_ALPHA" in str(m.get("content"))
                       for call in calls for m in call.get("messages", []))
        allowed = name not in ("deny", "ask-reject", "hidden")
        assert observed == allowed, (name, observed)
        assert events == (["entered", "approved", "read-done"] if allowed else ([] if name == "hidden" else ["entered"])), (name, events)
        assert host.request("GET", "/permission") == []
        if reset_after:
            host.request("POST", "/instance/dispose")
        result = {"case": name, "asked": asked, "events": events, "fixture_returned": observed, "passed": True}
        results.append(result)
        print(json.dumps(result), flush=True)
    assert fixture.read_text(encoding="utf-8") == "BOOK_PERMISSION_ALPHA\n"
finally:
    if host:
        host.close()
    model.shutdown()
    model.server_close()
    thread.join(timeout=5)
    report = {
        "version": version, "source_commit": support.COMMIT, "platform": "Windows x64",
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "cases": results, "passed": len(results) == 10,
        "fixture_unchanged": fixture.read_text(encoding="utf-8") == "BOOK_PERMISSION_ALPHA\n",
        "external_model_used": False,
        "fixtures": {name: hashlib.sha256((EXAMPLES / name).read_bytes()).hexdigest()
                     for name in ("read-fixture.ts", "check-tool-permissions.py", "check-host-plugins.py")},
    }
    support.write_json(root / "report.json", report)
    support.write_json(root / "model-requests.json", model.requests)
    print("Evidence:", root, flush=True)
