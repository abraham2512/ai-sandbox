.PHONY: init test-ci lint setup setup-rh-pre-commit install-uv install-shellcheck

install-uv:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }

install-shellcheck:
	@command -v shellcheck >/dev/null 2>&1 || { \
		echo "Installing shellcheck..."; \
		curl -sSL https://github.com/koalaman/shellcheck/releases/download/stable/shellcheck-stable.linux.x86_64.tar.xz | tar xJ --strip-components=1 -C /usr/local/bin shellcheck-stable/shellcheck; \
	}

init: install-uv setup-rh-pre-commit

test-ci: install-uv install-shellcheck lint

lint:
	uv run ruff check .
	uv run ruff format --check .
	find . -name '*.sh' -not -path '*/.venv/*' -not -path '*/.claude/worktrees/*' -not -path '*/node_modules/*' -print0 | xargs -0 -r shellcheck

setup:
	uv run pre-commit install

# VPN required for auth token login to RH internal pattern server
setup-rh-pre-commit: setup
	@echo "Installing rh-pre-commit hooks (requires VPN)..."
	uv run pre-commit run rh-pre-commit --all-files || true
	@echo "Installing rh-gitleaks into project venv..."
	uv pip install "rh-gitleaks @ git+https://gitlab.cee.redhat.com/infosec-public/developer-workbench/tools.git#subdirectory=rh-gitleaks"
	@echo "Logging in to rh-gitleaks pattern server..."
	uv run python3 -m rh_gitleaks login
