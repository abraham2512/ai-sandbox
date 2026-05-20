# RDS Policy Agent

AI-driven policy generation for OpenShift RDS version updates. Helps telco
partners update Day 2 configuration policies when moving between OCP versions
(e.g. 4.18 to 4.20).

See [docs/DESIGN.md](docs/DESIGN.md) for the full design document.

## Skill

The agent's domain knowledge is packaged as an
[Agent Skill](https://agentskills.io) at `skills/rds-policy-update/`,
with a Claude Code plugin wrapper for easy installation.

### Installing as a plugin (single session)

```sh
claude --plugin-dir /path/to/ai-sandbox/rds-policy
```

The skill is then available as `/rds-policy:rds-policy-update` and triggers
on prompts like "upgrade from 4.18 to 4.20" or "what changed between RDS
versions".

Note: `--plugin-dir` loads the plugin for the current session only. To
avoid typing it every time, add a shell alias:

```sh
alias claude-rds='claude --plugin-dir /path/to/ai-sandbox/rds-policy'
```

### Persistent installation via symlink

The plugin method above is session-scoped. For persistent availability
across all sessions, symlink the skill directly:

```sh
mkdir -p ~/.claude/skills
ln -s /path/to/ai-sandbox/rds-policy/skills/rds-policy-update ~/.claude/skills/rds-policy-update
```

This makes the skill available as `/rds-policy-update` in every Claude Code session.
