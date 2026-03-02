.PHONY: test-ci lint

test-ci: lint

lint:
	uv run ruff check .
	uv run ruff format --check .
