"""Read a project snapshot before or after its move into a parent repository."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import subprocess


class HistoryError(RuntimeError):
    """A Git operation failed, or a required historical file is unavailable."""


class RevisionFiles:
    def __init__(self, project_root: Path, revision: str):
        self.project_root = Path(project_root).resolve()
        self.revision = revision
        self.repository = Path(self._git(self.project_root, "rev-parse", "--show-toplevel")
                               .decode("utf-8").strip()).resolve()
        self.commit = self._git(self.repository, "rev-parse", "--verify", "--end-of-options",
                                f"{revision}^{{commit}}").decode("ascii").strip()
        prefix = self.project_root.relative_to(self.repository).as_posix()
        self.prefix = "" if prefix == "." else prefix
        if self.prefix:
            entry = self._entry(self.prefix)
            if entry is None:
                # Imported source commits stored this project at the Git root.
                self.prefix = ""
            elif entry[0] != "tree":
                raise HistoryError(f"{revision}:{self.prefix} is not a project directory")

    @staticmethod
    def _git(cwd: Path, *arguments: str) -> bytes:
        try:
            result = subprocess.run(["git", *arguments], cwd=cwd, capture_output=True, check=False)
        except OSError as exc:
            raise HistoryError(f"cannot run git in {cwd}: {exc}") from exc
        if result.returncode:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise HistoryError(f"git {arguments[0]} failed (exit {result.returncode}): {detail}")
        return result.stdout

    def _entry(self, path: str) -> tuple[str, str] | None:
        result = self._git(self.repository, "ls-tree", "-z", "--full-tree", self.commit,
                           "--", f":(literal){path}")
        records = [record for record in result.split(b"\0") if record]
        if not records:
            return None
        if len(records) != 1:
            raise HistoryError(f"ambiguous historical path: {self.revision}:{path}")
        metadata, _name = records[0].split(b"\t", 1)
        _mode, kind, object_id = metadata.decode("ascii").split()
        return kind, object_id

    def read_text(self, relative: str, *, missing_ok: bool = False) -> str | None:
        path = PurePosixPath(relative.replace("\\", "/"))
        if not relative or path.is_absolute() or ".." in path.parts or ":" in relative:
            raise HistoryError(f"expected a project-relative file path: {relative}")
        target = f"{self.prefix}/{path.as_posix()}" if self.prefix else path.as_posix()
        entry = self._entry(target)
        if entry is None:
            if missing_ok:
                return None
            raise HistoryError(f"cannot read {relative} at {self.revision}: file is absent ({target})")
        if entry[0] != "blob":
            raise HistoryError(f"{self.revision}:{target} is not a file")
        data = self._git(self.repository, "cat-file", "blob", entry[1])
        try:
            # Match the former subprocess text=True universal-newline behavior.
            return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError as exc:
            raise HistoryError(f"{self.revision}:{target} is not UTF-8 text") from exc
