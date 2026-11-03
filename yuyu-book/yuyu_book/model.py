"""BookModel: the shared shape every product reads instead of scraping HTML.

Phase P2 introduces the model before any renderer changes. The first slice is
deliberately small: the edition → part → unit → section → block spine plus one
diagnostic format, because a stable block ID is meaningless until there is a
block to hang it on. Terms, claims, sources and video types join when a
consumer needs them; empty placeholders would be dead weight.

Diagnostics are the only error format the migration adds:

    severity code file block_id message hint

`severity` is one of error/warning/info, `block_id` is "-" when the problem is
not attached to a block, and `hint` may be empty. Builders format the same way
whether the failure comes from a registry, a manuscript block or a PDF pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SEVERITIES = ("error", "warning", "info")


@dataclass(frozen=True, order=True)
class Diagnostic:
    severity: str
    code: str
    file: str
    block_id: str
    message: str
    hint: str = ""

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}, "
                             f"got {self.severity!r}")
        if not self.code:
            raise ValueError("diagnostic code must not be empty")
        if not self.message:
            raise ValueError("diagnostic message must not be empty")

    def __str__(self) -> str:
        parts = [self.severity, self.code, self.file or "-",
                 self.block_id or "-", self.message]
        if self.hint:
            parts.append(self.hint)
        return " ".join(parts)


@dataclass
class Block:
    """One citable unit of prose. `block_id` is empty until the author (or the
    migration) names it; `line` is 1-based and exists for diagnostics, never
    as an evidence key."""
    unit_id: str
    lang: str
    line: int
    kind: str          # paragraph | heading | list | table | quote | fence
    text: str
    block_id: str = ""
    end_line: int = 0               # inclusive; 0 means the single line


@dataclass
class Section:
    level: int
    title: str
    line: int
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Unit:
    id: str
    kind: str                       # front | chapter | appendix
    lang: str
    path: str
    title: str
    sections: list[Section] = field(default_factory=list)


@dataclass
class Part:
    id: str
    unit_ids: list[str] = field(default_factory=list)


@dataclass
class Edition:
    lang: str
    units: list[Unit] = field(default_factory=list)


@dataclass
class BookModel:
    editions: dict[str, Edition] = field(default_factory=dict)
    parts: list[Part] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
