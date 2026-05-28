# ImageBasedUpgrade (IBU) — Lifecycle Stages

The reference IBU lifecycle uses 3 stages, each in its own policy:

1. **Prep** — `stage: Prep`, includes `seedImageRef` (version + image),
   `oadpContent`, optional `extraManifests`
2. **Upgrade** — `stage: Upgrade`
3. **Finalize** — `stage: Idle` (returns to Idle after upgrade completes)

## Stage completeness check

Compare the partner's IBU stage policies against the reference. If the
partner is missing a stage the reference has, flag it as `[!]` for user
review — do not silently skip it. The user may have a valid reason for
omitting a stage, but they should confirm.

When adding a missing stage policy, apply the partner's naming
convention (version suffix, site suffix) to the new policy name.
