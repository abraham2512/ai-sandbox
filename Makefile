.PHONY: test-ci lint setup

test-ci: lint

lint:
	uv run ruff check .
	uv run ruff format --check .

setup:
	uv run pre-commit install
