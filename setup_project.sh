#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo "🚀 Initializing GenAI Project Structure..."

# 1. Create Directory Hierarchy [cite: 3]
echo "📂 Creating directories..."
mkdir -p src
mkdir -p tests
mkdir -p config
mkdir -p .streamlit

# 2. Create Authoritative Dependency File (pyproject.toml) 
# This defines dependencies and ruff configuration in one place.
echo "📄 Creating pyproject.toml..."
cat <<EOL > pyproject.toml
[project]
name = "streamlit-chatbot"
version = "0.1.0"
description = "Production-ready GenAI Chatbot"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "streamlit>=1.31.0",
    "langchain>=0.1.0",
    "langchain-openai>=0.0.8",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "tiktoken>=0.6.0"
]

[project.optional-dependencies]
dev = [
    "ruff>=0.3.0",
    "pytest>=8.0.0",
    "black>=24.0.0"
]

# Configure Ruff (Linting) [cite: 4]
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "W"] # Errors, Pyflakes, Imports, Warnings
ignore = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOL

# 3. Create Configuration File [cite: 11, 13]
# Centralizes model versions and retrieval parameters.
echo "⚙️ Creating config/app_config.yaml..."
cat <<EOL > config/app_config.yaml
app:
  title: "GenAI Support Bot"
  version: "1.0.0"

model:
  identifier: "gpt-3.5-turbo" # Can be swapped for gpt-4 or local models
  temperature: 0.7
  max_tokens: 500
  timeout: 10

memory:
  message_window: 5 # [cite: 81] Keep context across 5 turns
  
safety:
  forbidden_topics:
    - "financial advice"
    - "medical diagnosis"
EOL

# 4. Create the Makefile 
# Encapsulates workflows for reproducibility.
echo "🛠️ Creating Makefile..."
cat <<EOL > Makefile
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
	streamlit run src/ui.py

build:
	docker build -t streamlit-chatbot:latest .

# Placeholder for K8s deployment
deploy:
	@echo "Deploying to K8s..."
EOL

# 5. Create .gitignore (Critical for safety)
echo "🙈 Creating .gitignore..."
cat <<EOL > .gitignore
.env
__pycache__/
*.pyc
.venv/
.pytest_cache/
EOL

# 6. Create placeholder .env
echo "🔐 Creating .env.example..."
echo "OPENAI_API_KEY=replace_me" > .env.example

# 7. Create empty __init__.py files for package recognition
touch src/__init__.py
touch tests/__init__.py

# 8. Create dummy src/ui.py to verify 'make run' works later
echo "import streamlit as st" > src/ui.py
echo "st.title('GenAI Bot Placeholder')" >> src/ui.py

echo "✅ Project scaffolding complete!"
echo "👉 NEXT STEPS:"
echo "1. Run 'python3 -m venv .venv'"
echo "2. Run 'source .venv/bin/activate'"
echo "3. Run 'make bootstrap'"
EOL