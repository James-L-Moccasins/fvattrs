PYTHON_VERSIONS := 3.9 3.10 3.11 3.12 3.13 3.14
TEST_PY_TARGETS := $(addprefix test-py,$(PYTHON_VERSIONS))

.PHONY: sync lint format build test test-py test-all clean

sync:
	uv sync --all-groups

lint:
	uv run ruff check

format:
	uv run ruff format

build:
	uv build

test:
	uv run pytest

test-py%:
	uv run --python $* pytest

test-all: $(TEST_PY_TARGETS)

clean:
	rm -rf .venv .venv-* dist
	find . -name '*.egg-info' -prune -exec rm -rf {} +
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
