"""Run the pinned official EPUBCheck and record a portable result bound to the EPUB hash."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    version = subprocess.run([args.java, "-jar", str(args.jar), "--version"], capture_output=True, text=True, check=True)
    assert "5.3.0" in version.stdout + version.stderr, "Expected EPUBCheck 5.3.0"
    epub = ROOT / "deliverables/llm-explained-handdraw.epub"
    report = ROOT / "tmp/epubcheck-result.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([args.java, "-jar", str(args.jar), str(epub), "--json", str(report)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, "EPUBCheck failed"
    raw = json.loads(report.read_text(encoding="utf-8"))
    messages = raw.get("messages", [])
    # Warnings also fail the delivery gate; do not suppress the navigation check.
    problems = [message for message in messages if message.get("severity", "").upper() in ["FATAL", "ERROR", "WARNING"]]
    assert not problems, problems
    portable = {"checker": "EPUBCheck", "version": "5.3.0", "epubSha256": hashlib.sha256(epub.read_bytes()).hexdigest(), "status": "passed", "fatals": 0, "errors": 0, "warnings": 0}
    (ROOT / "deliverables/llm-epubcheck.json").write_text(json.dumps(portable, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(portable))


if __name__ == "__main__":
    run()
