#!/usr/bin/env bash
set -o errexit

PYTHON_BIN="${PYTHON_BIN:-python}"

if [ -x "./venv/bin/python" ]; then
  PYTHON_BIN="./venv/bin/python"
fi

"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" manage.py collectstatic --no-input
