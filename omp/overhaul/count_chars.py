from pathlib import Path
root = Path(__file__).resolve().parents[1]
rows = []
for p in sorted(root.glob("ch*.md")) + sorted(root.glob("appendix-*.md")):
    t = p.read_text(encoding="utf-8")
    rows.append((p.name, len(t), t.count("images/"), t.count("```mermaid")))
for name, n, img, mm in rows:
    print(f"{name}\t{n}\timg={img}\tmermaid={mm}")
