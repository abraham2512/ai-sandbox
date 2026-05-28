"""Structural assertions — multi-PG preservation and version bumps.

Promptfoo Python assertion return format (GradingResult):
    {"pass_": bool, "score": float 0-1, "reason": str}
    Snake_case keys auto-convert to camelCase.

CR replication (PTP interfaces) and patch preservation (StorageLV, NMState
removal) are handled by config-driven checks in merge.py:check_file_content.
"""

from common import (
    collect_manifests,
    collect_written_files,
    parse_pg_docs,
    version_matches,
)


def _fmt(name, passed, expected, actual):
    status = "PASS" if passed else "FAIL"
    return f"{status} {name} | EXPECTED: {expected} | ACTUAL: {actual}"


def check_yaml_nesting(_output, context):
    """Verify data/spec/status are siblings of metadata, not nested under it.

    The partner fixture includes a Secret with data incorrectly nested under
    metadata. The agent should fix this during merge. If data appears under
    metadata in any patch, the nesting is wrong.
    """
    written = collect_written_files(context)
    pg_docs, _ = parse_pg_docs(written)
    manifests = collect_manifests(pg_docs)

    issues = []
    for m in manifests:
        path = m.get("path", "?")
        for patch in m.get("patches", []):
            if not isinstance(patch, dict):
                continue
            meta = patch.get("metadata")
            if isinstance(meta, dict) and "data" in meta:
                issues.append(f"data nested under metadata in {path}")

    if issues:
        return {
            "pass_": False,
            "score": 0,
            "reason": f"YAML nesting issues: {'; '.join(issues)}",
        }
    return {
        "pass_": True,
        "score": 1.0,
        "reason": "No YAML nesting issues found in patches",
    }


def check_multi_pg_structure(_output, context):
    """Agent must preserve multi-PG file structure and apply version bumps to all."""
    config = context["config"]
    target_ver = config["target_version"]

    written = collect_written_files(context)
    pg_docs, _skipped = parse_pg_docs(written)

    checks = [
        (
            "multi_pg_preserved",
            len(pg_docs) >= 2,
            ">=2 PolicyGenerator files",
            f"found {len(pg_docs)} PG docs in {len(written)} written files",
        ),
    ]

    for i, pg in enumerate(pg_docs):
        pg_name = pg.get("metadata", {}).get("name", f"pg-{i}")
        ns = pg.get("policyDefaults", {}).get("namespace", "")
        label = (
            pg.get("policyDefaults", {})
            .get("placement", {})
            .get("labelSelector", {})
            .get("cluster-version", "")
        )

        checks.append(
            (
                f"name_bump_{pg_name}",
                version_matches(pg_name, target_ver),
                f"metadata.name contains {target_ver}",
                f"metadata.name='{pg_name}'",
            )
        )
        checks.append(
            (
                f"ns_bump_{pg_name}",
                version_matches(ns, target_ver),
                f"namespace contains {target_ver}",
                f"namespace='{ns}'",
            )
        )
        checks.append(
            (
                f"label_bump_{pg_name}",
                target_ver in label,
                f"cluster-version label contains {target_ver}",
                f"cluster-version='{label}'",
            )
        )

    total = len(checks)
    num_passed = sum(1 for _, passed, _, _ in checks if passed)

    return {
        "pass_": num_passed == total,
        "score": num_passed / total,
        "reason": f"{num_passed}/{total} multi-PG structure checks passed",
        "component_results": [
            {
                "pass_": bool(passed),
                "score": 1.0 if passed else 0.0,
                "reason": _fmt(name, passed, expected, actual),
            }
            for name, passed, expected, actual in checks
        ],
    }
