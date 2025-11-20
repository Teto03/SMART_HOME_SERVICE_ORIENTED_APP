#!/bin/bash
# Diagnostic script to check Python environment

echo "=== Python Version ==="
python3 --version

echo -e "\n=== Python Path ==="
which python3

echo -e "\n=== Flask Check ==="
python3 -c "import flask; print('✅ Flask found:', flask.__version__)" 2>&1

echo -e "\n=== Requests Check ==="
python3 -c "import requests; print('✅ Requests found:', requests.__version__)" 2>&1

echo -e "\n=== Python sys.path ==="
python3 -c "import sys; print('\n'.join(sys.path))"
