#!/bin/bash
# Diagnostic script to check Python environment

echo "=== Python Version ==="
./venv/bin/python3 --version

echo -e "\n=== Python Path ==="
which ./venv/bin/python3

echo -e "\n=== Flask Check ==="
./venv/bin/python3 -c "import flask; print('✅ Flask found:', flask.__version__)" 2>&1

echo -e "\n=== Requests Check ==="
./venv/bin/python3 -c "import requests; print('✅ Requests found:', requests.__version__)" 2>&1

echo -e "\n=== Dotenv Check ==="
./venv/bin/python3 -c "import dotenv; print('✅ Dotenv found:', dotenv.__file__)" 2>&1

echo -e "\n=== Python sys.path ==="
./venv/bin/python3 -c "import sys; print('\n'.join(sys.path))"
