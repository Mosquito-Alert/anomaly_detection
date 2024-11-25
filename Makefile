# Variables
PORT=8888  # Change this to the desired port if needed
NOTEBOOK_DIR=$(pwd)  # Default to the current directory

# Targets
.PHONY: start stop

start:
	@echo "Starting JupyterLab..."
	@jupyter lab --notebook-dir=$(NOTEBOOK_DIR) --port=$(PORT) & echo $$! > jupyterlab.pid
	@echo "JupyterLab started on port $(PORT)."

stop:
	@echo "Stopping JupyterLab..."
	@if [ -f jupyterlab.pid ]; then \
		kill $$(cat jupyterlab.pid) && rm -f jupyterlab.pid; \
		echo "JupyterLab stopped."; \
	else \
		echo "No JupyterLab process found."; \
	fi

