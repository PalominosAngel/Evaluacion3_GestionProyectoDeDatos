#!/usr/bin/env bash
# One-command launcher (macOS / Linux): creates the virtual environment on the
# first run, installs the dependencies and opens the dashboard in the browser.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON=""
for candidate in python3.14 python3.13 python3.12 python3.11 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
     && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: se requiere Python 3.11 o superior. Descárgalo desde https://www.python.org/downloads/" >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo ">> Creando entorno virtual con $($PYTHON --version)..."
  "$PYTHON" -m venv .venv
fi

# Reinstalls only when requirements.txt changed since the last successful install.
if [ ! -f .venv/.deps-ok ] || [ requirements.txt -nt .venv/.deps-ok ]; then
  echo ">> Instalando dependencias (solo la primera vez)..."
  .venv/bin/python -m pip install --quiet --upgrade pip
  .venv/bin/python -m pip install --quiet -r requirements.txt
  touch .venv/.deps-ok
fi

echo ">> Abriendo el dashboard en http://localhost:8501  (Ctrl+C para detenerlo)"
exec .venv/bin/python -m streamlit run dashboard/app.py --server.headless false
