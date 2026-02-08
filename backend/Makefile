.PHONY: help venv install dev clean test

help:
	@echo "Available commands:"
	@echo "  make venv     - Create virtual environment"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Start development server"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove virtual environment"

venv:
	python -m virtualenv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

install:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Creating..."; \
		make venv; \
	fi
	. venv/bin/activate && pip install -r requirements.txt

dev:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	./start_dev.sh

test:
	. venv/bin/activate && pytest

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
