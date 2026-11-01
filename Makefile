# Makefile: local environment and optional Postgres

.PHONY: setup clean-docker setup-venv install-deps start-db stop-db clean

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
