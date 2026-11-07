"""The Claim Ledger: assertions that rot, pinned to citable prose.

A claim is one fact the book asserts about a moving target -- a version, a
price, a count, a default, a performance number or a feature flag. Each claim
carries one `claim_id` shared by both editions, but locates itself separately
in each language: automatic block IDs are hashes over each file's text, so the
Chinese and English copies never pair by themselves.

The pairing rule is the point. The canonical `value` must appear inside both
quotes, so updating one edition to "2.1.311" while leaving the other at
"2.1.310" fails even though both quotes still exist. A quote that no longer
stands in its block fails the same way. The ledger cannot make an author keep
two manuscripts in sync, but it makes a one-sided edit impossible to merge
quietly.

Expiry has two severities. CI (`release=False`) reports a stale high-risk
claim as a warning; a release build refuses it. A retired claim is history:
its locators are no longer enforced, so removing the prose does not force a
rewrite of the ledger.

The file lives beside the other registries and is read through `registry.py`,
so its shape can migrate like everything else.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from . import blocks, registry
from .config import unit_stream
from .core import BuildError, read_text
from .model import Diagnostic
from .paths import REPO_ROOT

LEDGER = "claims.json"
MANUSCRIPT_LANGS = ("zh", "en")
KINDS = ("version", "price", "count", "default", "performance", "flag")
RISKS = ("high", "normal")
STATUSES = ("active", "retired")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def load() -> dict:
    return registry.load(LEDGER)


def manuscript_texts(manifest: dict, repo_root=REPO_ROOT,
                     langs=None) -> dict[str, dict[str, str]]:
    """{lang: {unit_id: markdown}} for every unit the manifest declares."""
    langs = list(langs or manifest.get("langs") or MANUSCRIPT_LANGS)
    texts: dict[str, dict[str, str]] = {lang: {} for lang in langs}
    for unit_def, _kind, _part in unit_stream(manifest):
        for lang in langs:
            if lang in unit_def:
                texts[lang][unit_def["id"]] = read_text(
                    repo_root / unit_def[lang])
    return texts


def _diag(severity: str, code: str, claim_id: str, message: str,
          hint: str = "") -> Diagnostic:
    return Diagnostic(severity, code, LEDGER, claim_id, message, hint)


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_day(value):
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def validate(ledger: dict, texts: dict, sources: dict, *,
             today: date | None = None, release: bool = False
             ) -> list[Diagnostic]:
    """Raise on every structural or locator error; return expiry warnings.

    `release=True` turns an expired high-risk claim into an error, because a
    release may not ship a fact the ledger already calls stale.
    """
    if not isinstance(ledger, dict):
        raise BuildError(str(_diag("error", "claims-shape", "",
                                   "claims.json must hold a JSON object")))
    entries = ledger.get("claims")
    if not isinstance(entries, list):
        raise BuildError(str(_diag("error", "claims-shape", "",
                                   "claims must be a JSON array")))
    today = today or date.today()
    errors: list[Diagnostic] = []
    warnings: list[Diagnostic] = []
    seen: set[str] = set()
    block_cache: dict[tuple[str, str], dict[str, str]] = {}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(_diag("error", "claim-shape", f"claims[{index}]",
                                "a claim must be a JSON object"))
            continue
        cid = entry.get("id")
        if not _text(cid) or not ID_RE.match(cid):
            errors.append(_diag(
                "error", "claim-id", str(cid or f"claims[{index}]"),
                "id must be a lowercase slug: [a-z][a-z0-9-]*"))
            cid = ""
        elif cid in seen:
            errors.append(_diag("error", "claim-id", cid,
                                "duplicate claim id"))
        else:
            seen.add(cid)

        kind = entry.get("kind")
        if kind not in KINDS:
            errors.append(_diag(
                "error", "claim-kind", cid,
                f"kind must be one of {', '.join(KINDS)}"))
        risk = entry.get("risk")
        if risk not in RISKS:
            errors.append(_diag(
                "error", "claim-risk", cid,
                f"risk must be one of {', '.join(RISKS)}"))
        status = entry.get("status")
        if status not in STATUSES:
            errors.append(_diag(
                "error", "claim-status", cid,
                f"status must be one of {', '.join(STATUSES)}"))
        value = entry.get("value")
        if not _text(value):
            errors.append(_diag("error", "claim-value", cid,
                                "value must be a non-empty string"))
        if not _text(entry.get("applies_to")):
            errors.append(_diag("error", "claim-scope", cid,
                                "applies_to must name the book version(s)"))
        source = entry.get("source")
        if not _text(source):
            errors.append(_diag("error", "claim-source", cid,
                                "source must name a sources.json entry"))
        elif source not in sources:
            errors.append(_diag("error", "claim-source", cid,
                                f"unknown source {source!r}"))
        verified = _parse_day(entry.get("verified"))
        if verified is None:
            errors.append(_diag("error", "claim-verified", cid,
                                "verified must be an ISO date (YYYY-MM-DD)"))
        review_days = entry.get("review_days")
        if (not isinstance(review_days, int) or isinstance(review_days, bool)
                or review_days <= 0):
            errors.append(_diag("error", "claim-review", cid,
                                "review_days must be a positive integer"))
            review_days = None

        if status == "retired":
            continue

        locators: dict[str, dict] = {}
        for lang in MANUSCRIPT_LANGS:
            loc = entry.get(lang)
            if not isinstance(loc, dict):
                errors.append(_diag("error", "claim-locator", cid,
                                    f"{lang} locator must be an object"))
                continue
            unit = loc.get("unit")
            block_id = loc.get("block")
            quote = loc.get("quote")
            missing = [name for name, got in
                       (("unit", unit), ("block", block_id), ("quote", quote))
                       if not _text(got)]
            if missing:
                errors.append(_diag(
                    "error", "claim-locator", cid,
                    f"{lang} locator needs {', '.join(missing)}"))
                continue
            if unit not in texts.get(lang, {}):
                errors.append(_diag(
                    "error", "claim-locator", cid,
                    f"unknown {lang} unit {unit!r}"))
                continue
            key = (lang, unit)
            if key not in block_cache:
                parsed = blocks.parse_blocks(texts[lang][unit], unit, lang)
                block_cache[key] = {b.block_id: b.text for b in parsed
                                    if b.block_id}
            body = block_cache[key].get(block_id)
            if body is None:
                errors.append(_diag(
                    "error", "claim-block", cid,
                    f"{lang}: no block {block_id!r} in {unit}",
                    "add the marker to the manuscript or fix the locator"))
                continue
            if quote not in body:
                errors.append(_diag(
                    "error", "claim-quote", cid,
                    f"{lang}: quote not found in {block_id}",
                    "the prose moved; re-anchor the claim"))
                continue
            if _text(value) and value not in quote:
                errors.append(_diag(
                    "error", "claim-value", cid,
                    f"{lang}: value {value!r} is absent from the quote",
                    "one edition was updated without the other"))
            locators[lang] = loc

        if (len(locators) == 2
                and locators["zh"]["unit"] != locators["en"]["unit"]):
            errors.append(_diag(
                "error", "claim-locator", cid,
                "zh and en locators name different units"))

        if (verified is not None and review_days is not None
                and status == "active"):
            try:
                due = verified + timedelta(days=review_days)
            except OverflowError:
                errors.append(_diag(
                    "error", "claim-review", cid,
                    "verified + review_days is outside the supported date range"))
                continue
            if today > due:
                message = (f"review was due on {due.isoformat()} "
                           f"({(today - due).days} days ago)")
                hint = "re-verify the value or set status to retired"
                if risk == "high":
                    severity = "error" if release else "warning"
                    (errors if release else warnings).append(_diag(
                        severity, "claim-expired", cid, message, hint))
                else:
                    warnings.append(_diag(
                        "warning", "claim-stale", cid, message, hint))

    if errors:
        raise BuildError("\n".join(str(error) for error in errors))
    return warnings
