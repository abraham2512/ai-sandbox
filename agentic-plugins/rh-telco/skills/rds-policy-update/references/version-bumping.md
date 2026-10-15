# Version Bumping and Sweeps

## Version Bumping

After processing all checklist items, walk the version-bumping section:
- Update `metadata.name` version suffixes in PolicyGenerator YAML
- Update `policyDefaults.namespace`
- Update `placement.labelSelector` version labels
- Update Namespace and ManagedClusterSetBinding resources
- For CatalogSource image tags: update those that track the OCP version.
  If a tag doesn't match the current version (partner pinned it to
  something else), flag as `[~] ⚠ REVIEW` in the checklist and
  preserve the partner's value.

## Semver Sweep

After version bumping, scan ALL output files — PolicyGenerator YAML,
kustomization.yaml, and any other written file — for any remaining
occurrence of the source OCP version (e.g. `4.18`, `4-18`, `4_18`).

**General rule:** every match is suspicious. If the value clearly tracks
the OCP version (channel, namespace suffix, annotation), update it.
If you're unsure whether a value tracks the OCP version, flag it in
the checklist as `[~] ⚠ REVIEW` and preserve the partner's value —
a false update can break partner-specific pinning.

Common locations this catches:
- `lca.openshift.io/target-ocp-version` annotations
- IBU `seedImageRef.version` and `seedImageRef.image`
- CatalogSource and operator index image tags
- Filenames referenced in kustomization.yaml generators/resources
- Hub template namespace references (`{{hub ... hub}}`)
- Channel values, label selectors, namespace suffixes

## Template ConfigMaps

ConfigMaps used as hub templates (referenced by `{{hub ... hub}}`
lookups) need the same namespace updates as CRs. If the version
bumping step changed CR namespaces, update the template ConfigMap
namespaces to match — lookups will break if the namespace is stale.

Also scan ConfigMap `data:` sections for version-bearing content
(e.g. catalog index tags, image references). Flag these with
`⚠ REVIEW` — they may need updating for the target version.

## Parent Kustomization

After creating the new version directory, update the `kustomization.yaml`
in the parent directory to add the new version directory to the
`generators:` or `resources:` list. Without this entry, kustomize
won't process the new version's policies.
