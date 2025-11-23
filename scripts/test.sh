#!/bin/bash

# Test script for Neura Call Center

set -e

echo "🧪 Running Neura Call Center Tests"
echo "=================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Activating virtual environment..."
    source venv/bin/activate || {
        echo "❌ Virtual environment not found. Creating one..."
        python -m venv venv
        source venv/bin/activate
        pip install -e ".[dev]"
    }
fi

echo "✅ Virtual environment activated"
echo ""

# Run linting
echo "🔍 Running linting..."
ruff check apps tests || {
    echo "⚠️  Linting issues found. Attempting to fix..."
    ruff check --fix apps tests
}

echo ""
echo "✅ Linting passed"
echo ""

# Run formatting check
echo "🎨 Checking code formatting..."
ruff format --check apps tests || {
    echo "⚠️  Formatting issues found. Fixing..."
    ruff format apps tests
}

echo ""
echo "✅ Formatting passed"
echo ""

# Run type checking
echo "🔎 Running type checking..."
mypy apps || echo "⚠️  Type checking found issues (non-blocking)"

echo ""

# Run tests
echo "🧪 Running tests..."
pytest -v --cov=apps --cov-report=term --cov-report=html

echo ""
echo "✅ All tests passed!"
echo ""
echo "📊 Coverage report generated in htmlcov/index.html"

