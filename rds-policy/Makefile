CONTAINER_RUNTIME := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)
IMAGE ?= rds-policy-agent:latest
BASE_IMAGE ?= lightspeed-agentic-sandbox:latest
PORT ?= 18080
CONTAINER_NAME ?= rds-policy-agent

CRED_ENVS = -e ANTHROPIC_API_KEY -e CLAUDE_CODE_USE_VERTEX \
            -e ANTHROPIC_VERTEX_PROJECT_ID -e CLOUD_ML_REGION

.PHONY: image run run-dev stop eval eval-skill clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

image: ## Build container image
	@$(CONTAINER_RUNTIME) inspect $(BASE_IMAGE) > /dev/null 2>&1 || \
		{ echo "Base image $(BASE_IMAGE) not found. Build from ../lightspeed-agentic-sandbox/"; exit 1; }
	$(CONTAINER_RUNTIME) build --build-arg BASE_IMAGE=$(BASE_IMAGE) -t $(IMAGE) .

run: image ## Start container and wait for health
	@$(CONTAINER_RUNTIME) run -d --rm --name $(CONTAINER_NAME) \
		-p $(PORT):8080 $(CRED_ENVS) $(IMAGE) > /dev/null
	@for i in $$(seq 1 30); do \
		curl -sf http://localhost:$(PORT)/health > /dev/null 2>&1 \
			&& { echo "Ready: http://localhost:$(PORT)"; exit 0; }; \
		sleep 1; \
	done; echo "ERROR: failed to start"; \
	$(CONTAINER_RUNTIME) logs $(CONTAINER_NAME) 2>&1 | tail -10; exit 1

run-dev: image ## Start with live skill mount (no rebuild needed on skill edits)
	@$(CONTAINER_RUNTIME) run -d --rm --name $(CONTAINER_NAME) \
		-p $(PORT):8080 $(CRED_ENVS) \
		-v ./rds_agent/skills:/app/skills:ro \
		$(IMAGE) > /dev/null
	@for i in $$(seq 1 30); do \
		curl -sf http://localhost:$(PORT)/health > /dev/null 2>&1 \
			&& { echo "Ready: http://localhost:$(PORT)"; exit 0; }; \
		sleep 1; \
	done; echo "ERROR: failed to start"; \
	$(CONTAINER_RUNTIME) logs $(CONTAINER_NAME) 2>&1 | tail -10; exit 1

stop: ## Stop and remove the running container
	@$(CONTAINER_RUNTIME) stop $(CONTAINER_NAME) 2>/dev/null || true
	@$(CONTAINER_RUNTIME) rm -f $(CONTAINER_NAME) 2>/dev/null || true

eval: run ## Smoke-test: POST to /v1/agent/run, then tear down
	@curl -sf -X POST http://localhost:$(PORT)/v1/agent/run \
		-H 'Content-Type: application/json' \
		-d '{"query": "hello, what can you do?"}' > /dev/null \
		&& echo "Smoke test passed" \
		|| { echo "Smoke test failed"; $(MAKE) stop; exit 1; }
	@$(MAKE) stop

eval-skill: ## Run promptfoo skill evals (no container needed)
	$(MAKE) -C evals eval

clean: stop ## Remove container image
	@$(CONTAINER_RUNTIME) rmi $(IMAGE) 2>/dev/null || true
	@echo "Cleaned $(IMAGE)"
