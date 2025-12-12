.PHONY: test lint format format-check typecheck

all: test lint format typecheck

test:
	$(info ****************** running tests ******************)
	uv run pytest tests

lint:
	$(info ****************** linting ******************)
	uv run pre-commit run -a

format:
	$(info ****************** formatting ******************)
	uv run ruff format

format-check:
	$(info ****************** checking formatting ******************)
	uv run ruff format --check

typecheck:
	$(info ****************** type checking ******************)
	uv run ty check src/fs_explorer/

build:
	$(info ****************** building ******************)
	uv build