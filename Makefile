# Simple Makefile for Contextual LLM Router

.PHONY: help setup clean-docker setup-venv install-deps start-db stop-db clean \
        exp01-full exp01-plot clean-exp01-plots check-status

# Setup targets
setup: clean-docker setup-venv install-deps start-db
	@echo "Setup complete!"

setup-venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv

install-deps:
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

start-db:
	@echo "Starting database containers..."
	docker-compose -f db/docker-compose-db.yaml up -d
	@echo "Waiting for database to be ready..."
	@sleep 25

stop-db:
	@echo "Stopping database containers..."
	docker-compose -f db/docker-compose-db.yaml down

clean-docker:
	@echo "Cleaning up Docker containers..."
	-docker-compose -f db/docker-compose-db.yaml down

clean: stop-db
	@echo "Cleaning up..."
	rm -rf venv
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Experiment targets (full runs)
exp01-full:
	@echo "Running Algorithm Comparison experiment..."
	./venv/bin/python -m experiments.X1_algorithm_comparison.run_experiment

# Plot-only targets (regenerate plots from existing data)
exp01-plot:
	@echo "Generating Algorithm Comparison plots..."
	./venv/bin/python -m experiments.X1_algorithm_comparison.plotting $(TS)

# Clean plot directories
clean-exp01-plots:
	@echo "Cleaning exp01 plots..."
	@rm -f experiments/X1_algorithm_comparison/plots/*.png experiments/X1_algorithm_comparison/plots/*.jpg

# Check status of running experiments
check-status:
	@echo "=== Running Screen Sessions ==="
	@screen -ls || echo "No screen sessions running"
	@echo ""
	@echo "Check logs in logs/ directory to see experiment progress."
