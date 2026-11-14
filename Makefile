# Makefile: local Python environment

.PHONY: setup setup-venv install-deps clean

setup: setup-venv install-deps
	@echo "Setup complete! Activate with: source venv/bin/activate"

setup-venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv

install-deps:
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

clean:
	@echo "Cleaning up..."
	rm -rf venv
	find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} +
