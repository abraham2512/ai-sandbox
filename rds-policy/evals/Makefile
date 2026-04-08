RDS_POLICY_DIR ?= $(shell cd .. && pwd)
EVAL_WORKDIR := /tmp/rds-eval-workdir

.PHONY: setup eval eval-view clean help

setup: ## Install eval dependencies
	npm install -g promptfoo
	npm install @anthropic-ai/claude-agent-sdk

eval: _prepare-workdir ## Run all evals
	RDS_POLICY_DIR=$(EVAL_WORKDIR) promptfoo eval -c promptfooconfig.yaml --no-cache

eval-view: ## View eval results in browser
	promptfoo view

clean: ## Clear eval cache and temp workdir
	promptfoo cache clear
	rm -rf $(EVAL_WORKDIR)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Create a clean working dir with only .claude/skills/ for skill discovery.
# Agent extracts/creates reference dirs on its own.
_prepare-workdir:
	@rm -rf $(EVAL_WORKDIR) /tmp/rds-explain-* /tmp/rds-merge-*
	@mkdir -p $(EVAL_WORKDIR)/.claude/skills
	@ln -s $(RDS_POLICY_DIR)/rds_agent/skills/rds-policy-update $(EVAL_WORKDIR)/.claude/skills/rds-policy-update
