# RDS Policy Agent

AI-driven policy generation for OpenShift RDS version updates. Helps telco
partners update Day 2 configuration policies when moving between OCP versions
(e.g. 4.18 to 4.20).

See [docs/DESIGN.md](docs/DESIGN.md) for the full design document.

## Quick Start

Install as a plugin from any repo — no cloning required:

```sh
/plugin marketplace add openshift-kni/ai-sandbox
/plugin install rds-policy@openshift-kni-ai-sandbox --project
```

This gives you the skill and the validation hook. Then prompt:

```
upgrade my policies from 4.18 to 4.20
```

### Prerequisites (optional, for validation hook)

- `kustomize` (v4.5+)
- [PolicyGenerator plugin](https://github.com/open-cluster-management-io/policy-generator-plugin)
  binary at `~/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator`

Without these, the skill works normally but the automatic validation
hook is a no-op. See [docs/HOOKS.md](docs/HOOKS.md) for details.

## Installation Options

The agent's domain knowledge is packaged as an
[Agent Skill](https://agentskills.io) at `skills/rds-policy-update/`.

### Plugin install (recommended)

Install from the marketplace into your project:

```sh
/plugin marketplace add openshift-kni/ai-sandbox
/plugin install rds-policy@openshift-kni-ai-sandbox --project  # team-shared
/plugin install rds-policy@openshift-kni-ai-sandbox --local    # personal only
```

Includes both the skill and the validation hook.

### Local development

Run Claude Code from `rds-policy/` for skill development:

```sh
cd rds-policy
claude
```

Or point to the plugin directory from any repo:

```sh
claude --plugin-dir /path/to/ai-sandbox/rds-policy
```


## Docs

- [DESIGN.md](docs/DESIGN.md) — architecture and design
- [EVAL.md](docs/EVAL.md) — eval plan and framework
- [HOOKS.md](docs/HOOKS.md) — validation hook details and what it catches
