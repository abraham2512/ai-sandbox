# RDS Policy Agent

AI-driven policy generation for OpenShift RDS version updates. Helps telco
partners update Day 2 configuration policies when moving between OCP versions
(e.g. 4.18 to 4.20).

See [docs/DESIGN.md](docs/DESIGN.md) for the full design document.

## Skill

The agent's domain knowledge is packaged as an
[Agent Skill](https://agentskills.io) at
`rds_agent/skills/rds-policy-update/`.

### Using with Claude Code

Symlink the skill into `.claude/skills/` for auto-discovery:

```sh
mkdir -p .claude/skills
ln -s ../../rds_agent/skills/rds-policy-update .claude/skills/rds-policy-update
```

Then start Claude Code from this directory. The skill triggers on prompts
like "upgrade from 4.18 to 4.20" or "what changed between RDS versions".

## Running as a Service

The agent runs on [lightspeed-agentic-sandbox](https://github.com/openshift/lightspeed-agentic-sandbox) —
a FastAPI service that wraps the Claude Agent SDK behind a REST endpoint. This
repo layers the RDS skill onto that base image.

### Prerequisites

Build the base image from the sibling repo:

```sh
podman build -t lightspeed-agentic-sandbox:latest \
    -f ../lightspeed-agentic-sandbox/Containerfile \
    ../lightspeed-agentic-sandbox/
```

### Build & Run

```sh
export ANTHROPIC_API_KEY=sk-...   # or use Vertex (see below)
make image    # builds rds-policy-agent:latest
make run      # starts on port 18080, waits for health
make stop     # tears down
```

### Query the Agent

```sh
curl -X POST http://localhost:18080/v1/agent/run \
    -H 'Content-Type: application/json' \
    -d '{"query": "explain what changed between RDS 4.18 and 4.20"}'
```

The endpoint returns:

```json
{"success": true, "summary": "...agent's response..."}
```

### Dev Mode (Live Skill Editing)

For development, `make run-dev` volume-mounts the skill directory so edits to
`SKILL.md` take effect without rebuilding:

```sh
make run-dev
```

### Vertex AI

To use Claude via Vertex instead of direct API:

```sh
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=your-project
export CLOUD_ML_REGION=us-east5
make run
```

### Evals

```sh
make eval-skill   # run promptfoo skill evals (no container needed)
make eval         # smoke-test: build, start, POST /v1/agent/run, stop
```
