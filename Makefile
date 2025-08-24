# Quiz App Backend Makefile

.PHONY: help install run test init clean

# Default target
help:
	@echo "Quiz App Backend - Available Commands:"
	@echo ""
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the FastAPI server"
	@echo "  test       - Run API tests"
	@echo "  init       - Initialize database with sample data"
	@echo "  clean      - Clean up database and cache files"
	@echo "  docs       - Open API documentation in browser"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Run the server
run:
	@echo "🚀 Starting Quiz App Backend..."
	python run.py

# Run tests
test:
	@echo "🧪 Running API tests..."
	python test_api.py

# Initialize database with sample data
init:
	@echo "🗄️  Initializing database..."
	python init_db.py

# Clean up files
clean:
	@echo "🧹 Cleaning up..."
	rm -f quiz_app.db
	rm -rf __pycache__
	rm -rf .pytest_cache
	@echo "✅ Cleanup completed!"

# Open API documentation
docs:
	@echo "📖 Opening API documentation..."
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:8000/docs; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:8000/docs; \
	else \
		echo "Please open http://localhost:8000/docs in your browser"; \
	fi

# Development mode with auto-reload
dev:
	@echo "🔧 Starting development server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Check server status
status:
	@echo "🔍 Checking server status..."
	@curl -s http://localhost:8000/ > /dev/null && echo "✅ Server is running" || echo "❌ Server is not running"

# Full setup (install + run + init)
setup: install
	@echo "🎯 Setup completed! Run 'make run' to start the server"
