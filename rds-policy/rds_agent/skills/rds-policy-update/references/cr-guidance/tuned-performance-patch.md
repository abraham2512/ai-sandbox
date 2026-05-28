# TunedPerformancePatch — Restructure Guidance

Between 4.18 and 4.20 the reference TunedPerformancePatch changed from
a single profile to 4 architecture-specific profiles:

- `ran-du-performance` — top-level, includes `ran-du-performance-architecture-common`
- `ran-du-performance-architecture-common` — cross-arch settings
- `ran-du-common-aarch64` — ARM-specific
- `ran-du-common-x86` — x86-specific

## Content accounting

When restructuring a partner's single-profile Tuned into the new
multi-profile layout, account for EVERY section in the partner's
original data block: `[main]`, `[sysctl]`, `[scheduler]`, `[service]`,
`[bootloader]`. After writing the merged patches, list which partner
section ended up in which profile. If any section from the partner's
input is not present in any output profile, you dropped content — add
it back to the correct profile immediately.

Typical placement:
- `[sysctl]` partner entries → `ran-du-performance-architecture-common`
- `[scheduler]` partner entries → `ran-du-common-x86` (x86-specific)
- `[service]` partner entries → `ran-du-performance-architecture-common`
- `[bootloader]` partner entries → `ran-du-common-x86` (x86-specific)

## Other changes

- Profile name: `performance-patch` → `ran-du-performance`
- Priority: 19 → 18
