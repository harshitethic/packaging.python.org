"""Fail CI when Sphinx reports a broken link on a line added by a PR."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _added_lines(base: str) -> dict[str, set[int]]:
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--unified=0",
            "--no-color",
            f"{base}...HEAD",
            "--",
            "*.rst",
            "*.md",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    added: dict[str, set[int]] = defaultdict(set)
    current_path: str | None = None

    for line in completed.stdout.splitlines():
        if line.startswith("+++ b/"):
            current_path = line.removeprefix("+++ b/")
            continue
        if not line.startswith("@@") or current_path is None:
            continue

        match = HUNK_RE.match(line)
        if match is None:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        added[current_path].update(range(start, start + count))

    return dict(added)


def _normalize_source_path(filename: str) -> str:
    path = Path(filename)
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        normalized = path.as_posix()
        if normalized.startswith("source/"):
            return normalized
        return f"source/{normalized.lstrip('/')}"


def _new_broken_links(
    report: Path, added_lines: dict[str, set[int]]
) -> list[tuple[str, int, str, str]]:
    failures: list[tuple[str, int, str, str]] = []
    if not report.exists():
        return failures

    with report.open(encoding="utf-8") as lines:
        for raw_line in lines:
            entry = json.loads(raw_line)
            if entry.get("status") not in {"broken", "malformed"}:
                continue

            filename = entry.get("filename")
            lineno = entry.get("lineno")
            uri = entry.get("uri")
            if not isinstance(filename, str) or not isinstance(lineno, int):
                continue

            source_path = _normalize_source_path(filename)
            if lineno not in added_lines.get(source_path, set()):
                continue

            failures.append(
                (
                    source_path,
                    lineno,
                    str(uri or ""),
                    str(entry.get("info") or entry.get("code") or ""),
                )
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="PR base commit SHA")
    parser.add_argument("--report", type=Path, default=Path("build/output.json"))
    args = parser.parse_args()

    added_lines = _added_lines(args.base)
    failures = _new_broken_links(args.report, added_lines)

    if not failures:
        print("No newly added broken links found.")
        return 0

    print("Broken links were added by this pull request:")
    for path, line, uri, info in failures:
        detail = f" ({info})" if info else ""
        print(f"- {path}:{line}: {uri}{detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
