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
    """Verify the agent did not deepen pre-existing nesting errors.

    The partner fixture has AcmeMonitoring patches with data nested under
    metadata (a pre-existing bug). Per CNF-23302, the skill should preserve
    the partner's original structure and flag as a pre-existing issue — not
    fix it. This assertion checks that the agent did not make nesting WORSE
    (e.g. adding additional keys under metadata that weren't there before).
    """
    written = collect_written_files(context)
    pg_docs, _ = parse_pg_docs(written)
    manifests = collect_manifests(pg_docs)

    known_preexisting = {"AcmeMonitoring"}
    new_issues = []
    for m in manifests:
        path = m.get("path", "?")
        for patch in m.get("patches", []):
            if not isinstance(patch, dict):
                continue
            meta = patch.get("metadata")
            if not isinstance(meta, dict) or "data" not in meta:
                continue
            if any(known.lower() in path.lower() for known in known_preexisting):
                continue
            new_issues.append(f"data nested under metadata in {path}")

    if new_issues:
        return {
            "pass_": False,
            "score": 0,
            "reason": f"New YAML nesting issues (not pre-existing): {'; '.join(new_issues)}",
        }
    return {
        "pass_": True,
        "score": 1.0,
        "reason": "No new YAML nesting issues — pre-existing issues preserved as expected",
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
