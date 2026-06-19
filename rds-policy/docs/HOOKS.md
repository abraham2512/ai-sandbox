# PolicyGenerator Validation Hook

A Claude Code PostToolUse hook that validates PolicyGenerator YAML after every
Write/Edit. Runs `kustomize build --enable-alpha-plugins` to catch structural
errors before the user reviews the output.

## Why

The skill generates PolicyGenerator YAML during MERGE. Without validation, the
LLM can produce output with missing source-cr paths, stale references, or
invalid field combinations — errors that only surface when someone runs
`kustomize build` manually. The hook makes this automatic: errors feed back to
the LLM via exit code 2, and it self-corrects in the same turn.

## How it works

```
Skill writes PolicyGenerator YAML
  → hook fires (PostToolUse on Write/Edit of *.yaml)
  → checks for `kind: PolicyGenerator` in the file
  → runs `kustomize build --enable-alpha-plugins` on the directory
  → exit 0 + "VALIDATE OK"  (success, shown in transcript)
  → exit 2 + error on stderr (fed back to LLM for self-correction)
```

The hook only fires on `.yaml` files containing `kind: PolicyGenerator`. All
other files are a silent no-op.

## Example: feedback loop in action

During a MERGE run, the skill edits a PolicyGenerator file incrementally.
The hook catches that `ClusterMonitoringConfig.yaml` no longer exists in the
4.20 source-crs:

```
⏺ Edit(acme-sno-4.20.yaml)                    # skill swaps ICSP → IDMS path
  ⎿  PostToolUse:Edit hook returned blocking error
     VALIDATE FAILED — kustomize build errors:
     could not read the manifest path source-crs/ClusterMonitoringConfig.yaml
     in policy acme-sno-config-policy
```

The LLM reads the error and adapts — instead of continuing with incremental
edits (each of which would fail), it writes the complete merged file in one
pass with all path changes applied:

```
⏺ Write(acme-sno-4.20.yaml)                   # skill writes complete file
  ⎿  VALIDATE OK — PolicyGenerator build passed
```

No human intervention needed. The hook taught the LLM to produce valid output.

## What the validation catches (and doesn't)

`kustomize build` + the PolicyGenerator plugin binary perform these checks
implicitly:

| Check | Caught? | Example error |
|-------|---------|---------------|
| Missing source-cr path | Yes | `could not read the manifest path source-crs/DoesNotExist.yaml` |
| Malformed YAML syntax | Yes | `MalformedYAMLError: yaml: line 21: did not find expected '-' indicator` |
| Duplicate YAML keys | Yes | `mapping key "namespace" already defined at line 6` |
| Unknown PG fields | Yes | `field bogusField found but not defined in type PolicyGenerator` |
| Invalid field combos | Yes | `field consolidateManifests found but not defined` (wrong level) |
| Stale kustomization.yaml refs | Yes | `could not read the manifest path` (old filename) |
| Invalid complianceType value | **No** | Passes silently — `bogus` accepted |
| Invalid remediationAction | **No** | Passes silently — `bogus` accepted |
| Bad fields inside source-cr patches | **No** | `totallyFakeField: true` passes — PG doesn't validate embedded CRs |
| Wrong apiVersion in source-crs | **No** | `ptp.openshift.io/v999` passes — PG passes through any content |

**Bottom line:** the hook catches structural and YAML issues reliably. It does
not validate the content of embedded CRs or enum field values — those require
either `kubeconform` with CRD schemas or `oc apply --dry-run=server` against
a real cluster.

## Prerequisites

- `kustomize` (v4.5+)
- PolicyGenerator plugin binary at:
  `~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator`

The hook degrades to a no-op if either tool is missing.

## Files

| File | Purpose |
|------|---------|
| `.claude/hooks/validate-policygen.sh` | The hook script |
| `.claude/settings.json` | Wires up the PostToolUse hook |

## Linting

The hook script is checked by `shellcheck` as part of `make lint` from the
repo root.
