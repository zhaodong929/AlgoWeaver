.PHONY: install test lint format demo

install:
	uv sync --group dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

demo:
	uv run algo-weaver extract --input examples/moving_average/algorithm.md --output data/processed/moving_average_capability.json --mode mock
