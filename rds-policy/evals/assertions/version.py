"""Version assertions — semver sweep and version-bearing field checks.

Promptfoo Python assertion return format (GradingResult):
    {"pass_": bool, "score": float 0-1, "reason": str}
    Snake_case keys auto-convert to camelCase.
"""

import re

from common import collect_written_files, parse_pg_docs


def check_semver_sweep(_output, context):
    """No source version string should remain in the output PolicyGenerator files.

    Scans all written PG YAML files for the source OCP version (e.g. "4.18").
    Any remaining occurrence indicates the agent missed a version bump.
    Matches both dotted (4.18) and hyphenated (4-18) forms.
    """
    config = context.get("config") or {}
    source_version = config.get("source_version", "4.18")

    written = collect_written_files(context)
    if not written:
        return {
            "pass_": False,
            "score": 0,
            "reason": "No written files found",
        }

    pg_docs, _ = parse_pg_docs(written)
    if not pg_docs:
        return {
            "pass_": False,
            "score": 0,
            "reason": "No PolicyGenerator docs found in written files",
        }

    parts = source_version.split(".")
    if len(parts) < 2:
        return {
            "pass_": False,
            "score": 0,
            "reason": f"Invalid source_version '{source_version}' (expected major.minor)",
        }
    major, minor = parts[0], parts[1]
    patterns = [
        re.compile(rf"{major}\.{minor}(?!\d)"),
        re.compile(rf"{major}-{minor}(?!\d)"),
        re.compile(rf"{major}_{minor}(?!\d)"),
    ]

    hits = []
    for filepath, content in written.items():
        if filepath.endswith(".md"):
            continue
        for line_num, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            value_part = re.split(r"\s+#\s", line, maxsplit=1)[0]
            for pat in patterns:
                if pat.search(value_part):
                    hits.append(f"{filepath}:{line_num}: {stripped[:100]}")

    if hits:
        return {
            "pass_": False,
            "score": max(0, 1 - len(hits) / 10),
            "reason": f"Source version {source_version} found in {len(hits)} lines",
            "component_results": [
                {"pass_": False, "score": 0, "reason": h} for h in hits[:10]
            ],
        }

    return {
        "pass_": True,
        "score": 1.0,
        "reason": f"No source version {source_version} found in output files",
    }
