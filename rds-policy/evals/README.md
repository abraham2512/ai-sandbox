# Evals

Evaluations for the RDS policy agent skill using [promptfoo](https://promptfoo.dev)
with the Claude Agent SDK provider.

## Setup

```bash
make setup
```

## Running

```bash
# Run all tests
make eval

# Run a single test by description
make eval-single FILTER="EXPLAIN identifies"

# Check consistency (run 3 times)
promptfoo eval -c promptfooconfig.yaml --repeat 3
```

## Viewing Results

```bash
# Browser UI — shows detailed results, diffs, assertion details
make eval-view

# List all past runs
make eval-history

# Export results to JSON
make eval-export
```

## Test Categories

| Category | What it checks |
|---|---|
| Triggering | Skill activates on right prompts, doesn't over-trigger |
| EXPLAIN | Reference diff accuracy, no false asks for policies |
| Workflow | EXPLAIN before MERGE, no filesystem exploration |
| Safety | No kubectl apply without dry-run |

## After Changing the Skill

1. Make your changes to `SKILL.md` or `references/`
2. Run `make eval`
3. Run `make eval-view` to compare with previous runs
4. If tests fail, decide: fix the skill or fix the assertion

## Adding Tests

Add new test cases to `promptfooconfig.yaml`. Each test has:
- `description` — what it tests
- `vars.prompt` — the user prompt
- `assert` — list of assertions (see [promptfoo assertions](https://promptfoo.dev/docs/configuration/expected-outputs))

Common assertion types:
- `skill-used` / `not-skill-used` — did the skill trigger?
- `icontains` / `not-icontains` — output contains/doesn't contain text
- `icontains-any` — output contains at least one of the values
- `javascript` — custom check on output or tool calls

## Notes

- Each test runs in an isolated Claude Code session (~2-3 min per test)
- Results are stored locally by promptfoo, not in git
- `make eval-view` shows history across all runs
