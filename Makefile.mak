.PHONY: help install install-dev test clean uninstall

help:
	@echo "XRF Analysis Package - Available Commands"
	@echo "=========================================="
	@echo "make install        - Install package"
	@echo "make install-dev    - Install in development mode"
	@echo "make test          - Run installation tests"
	@echo "make clean         - Remove build artifacts"
	@echo "make uninstall     - Uninstall package"
	@echo ""
	@echo "After installation, use: xrf-analyze --help"

install:
	pip install .

install-dev:
	pip install -e .

test:
	python test_installation.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

uninstall:
	pip uninstall -y xrf-analysis