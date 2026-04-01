#!/bin/bash
# Backend development scripts
# Usage: bash scripts.sh <command>

case "$1" in
  lint)
    ruff check app/ tests/
    ;;
  lint-fix)
    ruff check --fix app/ tests/
    ;;
  format)
    ruff format app/ tests/
    ;;
  type-check)
    mypy app/ --ignore-missing-imports
    ;;
  test)
    TESTING=1 python -m pytest tests/ -v --tb=short
    ;;
  test-cov)
    TESTING=1 python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
    ;;
  seed)
    python -c "import asyncio; from app.scripts.seed_data import seed; asyncio.run(seed())"
    ;;
  migrate)
    alembic upgrade head
    ;;
  *)
    echo "Usage: bash scripts.sh {lint|lint-fix|format|type-check|test|test-cov|seed|migrate}"
    exit 1
    ;;
esac
