"""Manifest/source configuration: shape validation and ordered traversal."""
from __future__ import annotations

import re

from .diagnostics import BuildError
from .paths import REPO_ROOT
from .text import HAN_RE

GUIDE_FIELDS = ("question", "deliverable", "boundary")
SOURCE_REQUIRED = ("title", "authority", "kind", "url", "snapshot",
                   "accessed", "license", "scope")
SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# registry text the book authored for itself, and therefore owes in both languages
MIRRORED_FIELDS = ("title", "authority", "snapshot", "license", "scope")


def expected_ids(manifest: dict) -> list[str]:
    ids = [manifest["front"]["id"]]
    for part in manifest["parts"]:
        ids.extend(u["id"] for u in part["units"])
    ids.extend(a["id"] for a in manifest["appendices"])
    return ids


def unit_stream(manifest: dict):
    """Yield (unit_def, kind, part) in book order."""
    yield manifest["front"], "front", None
    for part in manifest["parts"]:
        for unit in part["units"]:
            yield unit, "chapter", part
    for apx in manifest["appendices"]:
        yield apx, "appendix", None


def validate_configs(manifest: dict, sources: dict) -> None:
    errors: list[str] = []
    ids = expected_ids(manifest)
    if len(ids) != len(set(ids)):
        errors.append("duplicate unit ids in manifest")

    langs = list(manifest.get("langs") or ("zh", "en"))
    for unit_def, kind, _part in unit_stream(manifest):
        for lang in langs:
            if lang not in unit_def:
                errors.append(f"unit {unit_def['id']}: missing {lang} path key")
                continue
            p = REPO_ROOT / unit_def[lang]
            if not p.exists():
                errors.append(f"unit {unit_def['id']}: missing {lang} file "
                              f"{unit_def[lang]}")

    guides = manifest.get("guides", {})
    plain_optional = bool(manifest.get("plain_optional"))
    if plain_optional and not guides:
        pass
    else:
        if set(guides) != set(ids):
            missing = sorted(set(ids) - set(guides))
            extra = sorted(set(guides) - set(ids))
            if missing:
                errors.append(f"guides missing for: {', '.join(missing)}")
            if extra:
                errors.append(f"guides for unknown units: {', '.join(extra)}")
        for uid, guide in guides.items():
            for f in GUIDE_FIELDS:
                entry = guide.get(f) or {}
                for lang in langs:
                    if not (entry.get(lang) or "").strip():
                        errors.append(f"guide {uid}.{f}.{lang} is empty")
            for sid in guide.get("sources", []):
                if sid not in sources:
                    errors.append(f"guide {uid}: unknown source id {sid!r}")

    for sid, src in sources.items():
        if not SOURCE_ID_RE.match(sid):
            errors.append(f"source id {sid!r} not [a-z0-9-]+")
        for f in SOURCE_REQUIRED:
            if not str(src.get(f, "")).strip():
                errors.append(f"source {sid}: field {f} missing/empty")
        url = src.get("url", "")
        if not url.startswith("https://"):
            errors.append(f"source {sid}: url must be https")
        kind = src.get("kind")
        pinned = src.get("pinned") or {}
        if kind == "github" and not (pinned.get("tag") or pinned.get("commit")):
            errors.append(f"source {sid}: github refs must pin tag or commit")
        if kind == "npm" and not pinned.get("version"):
            errors.append(f"source {sid}: npm refs must pin version")
        if kind == "community" and (src.get("normative") is not False
                                    or not src.get("accessed")):
            errors.append(f"source {sid}: community refs need "
                          "normative:false + accessed date")
        if kind == "community" and pinned.get("commit"):
            if len(pinned["commit"]) < 40:
                errors.append(f"source {sid}: commit must be full sha")
        # Everything below is text *we* wrote about a source, not text from it,
        # so the English edition owns an English copy of it: a forum thread's
        # Chinese title is searchable by URL and post id, and an English reader
        # deserves to know what it says.
        for field in MIRRORED_FIELDS:
            value = str(src.get(field, ""))
            mirror = str(src.get(f"{field}_en", ""))
            if HAN_RE.search(value) and not mirror.strip():
                errors.append(f"source {sid}: {field} carries Chinese, so it "
                              f"needs {field}_en for the English edition")
            if mirror and HAN_RE.search(mirror):
                errors.append(f"source {sid}: {field}_en still carries Chinese")

    if errors:
        raise BuildError("config invalid:\n  " + "\n  ".join(errors))


def load_configs(manifest_name: str = "manifest.json",
                 sources_name: str = "sources.json"):
    from . import registry
    manifest = registry.load(manifest_name)
    sources = registry.load(sources_name)
    validate_configs(manifest, sources)
    return manifest, sources
