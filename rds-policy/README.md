# RDS Policy Agent

AI-driven policy generation for OpenShift RDS version updates. Helps telco
partners update Day 2 configuration policies when moving between OCP versions
(e.g. 4.18 to 4.20).

See [docs/DESIGN.md](docs/DESIGN.md) for the full design document.

## Quick Start

Run Claude Code from `rds-policy/`:

```sh
cd rds-policy
claude
```

The skill triggers on prompts like "upgrade from 4.18 to 4.20" or "what
changed between RDS versions". A validation hook runs `kustomize build`
after every PolicyGenerator edit to catch errors automatically.

### Prerequisites (optional, for validation hook)

- `kustomize` (v4.5+)
- [PolicyGenerator plugin](https://github.com/open-cluster-management-io/policy-generator-plugin)
  binary at `~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator`

Without these, the skill works normally but the automatic validation
hook is a no-op. See [docs/HOOKS.md](docs/HOOKS.md) for details.

## Skill

The agent's domain knowledge is packaged as an
[Agent Skill](https://agentskills.io) at `rds_agent/skills/rds-policy-update/`.

### Local usage (skill + validation hook)

When running from `rds-policy/`, you get both the skill (via
`.claude/skills/` symlink) and the validation hook (via
`.claude/settings.json`). This is the recommended setup.

### Plugin usage (skill only)

```sh
claude --plugin-dir /path/to/ai-sandbox/rds-policy
```

This loads the skill as `/rds-policy:rds-policy-update` but does not
include the validation hook — hooks are not part of the plugin spec.

### Global installation via symlink

```sh
mkdir -p ~/.claude/skills
ln -s /path/to/ai-sandbox/rds-policy/rds_agent/skills/rds-policy-update ~/.claude/skills/rds-policy-update
```

This makes the skill available in every Claude Code session as
`/rds-policy-update`. No validation hook.

## Docs

- [DESIGN.md](docs/DESIGN.md) — architecture and design
- [EVAL.md](docs/EVAL.md) — eval plan and framework
- [HOOKS.md](docs/HOOKS.md) — validation hook details and what it catches
