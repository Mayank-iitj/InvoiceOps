#!/usr/bin/env bash
set -e

echo "=================================================="
echo " Starting InvoiceOps Server (Production / Dev)"
echo "=================================================="

# Check Python availability
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found."
    exit 1
fi

$PYTHON_CMD run_app.py

