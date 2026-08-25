PYTHON := uv run python
CONFIG ?= config.json

.PHONY: install run debug clean lint test

install:
	uv sync

run:
	$(PYTHON) pac-man.py "$(CONFIG)"

debug:
	$(PYTHON) -m pdb pac-man.py "$(CONFIG)"

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
	find . -path ./.venv -prune -o -type f \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} +

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

test:
	$(PYTHON) -m unittest discover -s tests -v