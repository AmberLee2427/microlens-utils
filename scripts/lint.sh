#!/usr/bin/env bash
# Run Ruff format and lint checks consistently.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "Running Ruff formatter check..."
ruff format --check .

echo "Running Ruff lint..."
ruff check .
