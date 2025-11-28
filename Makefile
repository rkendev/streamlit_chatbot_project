.PHONY: help bootstrap lint test run build deploy

help:
	@echo "Available commands:"
	@echo "  make bootstrap  - Install dependencies in venv"
	@echo "  make lint       - Run ruff linter [cite: 4]"
	@echo "  make test       - Run unit tests [cite: 19]"
	@echo "  make run        - Run local Streamlit app"
	@echo "  make build      - Build Docker image"

bootstrap:
	pip install -e .[dev]

lint:
	ruff check .

test:
	pytest tests/

run:
	PYTHONPATH=. streamlit run src/ui.py
	
build:
	docker build -t streamlit-chatbot:latest .

# Placeholder for K8s deployment
deploy:
	@echo "Deploying to K8s..."
