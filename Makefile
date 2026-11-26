# ===============================
# Project settings
# ===============================
PY_SRCS = delivery
RADON_MIN_MI = 65

# ===============================
# Phony targets
# ===============================
.PHONY: help lint fmt type security cc mi radon-check hal raw check

help:
	@echo "Available commands:"
	@echo "  lint         - ruff check --fix"
	@echo "  fmt          - ruff format"
	@echo "  type         - mypy"
	@echo "  security     - bandit"
	@echo "  cc           - radon cc"
	@echo "  mi           - radon mi"
	@echo "  radon-check  - quality gates (CC + MI)"
	@echo "  hal          - radon hal"
	@echo "  raw          - radon raw"
	@echo "  check        - full check"

# ===============================
# Ruff
# ===============================
lint:
	uv run ruff check $(PY_SRCS) --fix

fmt:
	uv run ruff format $(PY_SRCS)

# ===============================
# Mypy
# ===============================
type:
	uv run mypy $(PY_SRCS)

# ===============================
# Bandit
# ===============================
security:
	uv run bandit -r $(PY_SRCS) -lll -x .venv,venv,build,dist,migrations

# ===============================
# Radon
# ===============================
cc:
	uv run radon cc -s -a $(PY_SRCS)

mi:
	uv run radon mi $(PY_SRCS)

hal:
	uv run radon hal $(PY_SRCS)

raw:
	uv run radon raw $(PY_SRCS)

radon-check:
	@uv run python scripts/check_radon.py $(PY_SRCS)

# ===============================
# Combined
# ===============================
check: lint fmt type security radon-check