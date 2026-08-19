.PHONY: install run debug clean lint lint-strict
SRC = classes.py parser.py main.py graph.py pathfinder.py scheduler.py visualizer.py
install:
	@uv sync

run:
	@python3 main.py $(filter-out $@,$(MAKECMDGOALS))

debug:
	@python3 -m pdb main.py $(filter-out $@,$(MAKECMDGOALS))

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	@flake8 $(SRC)
	@mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

%:
	@: