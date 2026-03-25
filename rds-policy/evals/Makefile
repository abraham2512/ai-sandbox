.PHONY: setup eval eval-view clean

setup: ## Install eval dependencies
	npm install -g promptfoo
	npm install @anthropic-ai/claude-agent-sdk

eval: ## Run all evals
	promptfoo eval -c promptfooconfig.yaml

eval-view: ## View eval results in browser
	promptfoo view

clean: ## Clear eval cache
	promptfoo cache clear

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
