.PHONY: test unit_testperf_coverage lint doc 

test: 
	python -m pytest

unit_test: 
	python -m pytest -m "not performance"

perf_test: 
	python -m pytest -m "performance"

coverage: 
	python -m coverage run --branch -m pytest -m "not performance"
	python -m coverage report -m
	python -m coverage html

lint:
	python -m ruff check 

doc: 
	python -m doc --html --output-dir html triangulator