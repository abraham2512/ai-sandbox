#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook: validates PolicyGenerator YAML after Write/Edit
# Input: JSON via stdin with tool_name, tool_input, tool_result
# Output: exit 0 = success (stdout in transcript), exit 2 = error (stderr fed back to Claude)

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Only validate YAML files
case "$FILE_PATH" in
  *.yaml|*.yml) ;;
  *) exit 0 ;;
esac

# Check if this file is a PolicyGenerator
if ! grep -q 'kind: PolicyGenerator' "$FILE_PATH" 2>/dev/null; then
  exit 0
fi

DIR=$(dirname "$FILE_PATH")

# Need kustomization.yaml in the same directory
if [ ! -f "$DIR/kustomization.yaml" ]; then
  exit 0
fi

if ! command -v kustomize &>/dev/null; then
  exit 0
fi

PG_PLUGIN="${HOME}/.config/kustomize/plugin/policy.open-cluster-management.io/v1/policygenerator/PolicyGenerator"
if [ ! -x "$PG_PLUGIN" ]; then
  exit 0
fi

# Validate: kustomize build with PolicyGenerator plugin
BUILD_OUTPUT=$(kustomize build --enable-alpha-plugins "$DIR" 2>&1) || {
  echo "VALIDATE FAILED — kustomize build errors:" >&2
  echo "$BUILD_OUTPUT" >&2
  exit 2
}

echo "VALIDATE OK — PolicyGenerator build passed"
exit 0
