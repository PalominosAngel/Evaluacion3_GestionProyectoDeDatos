@echo off
REM One-command launcher (Windows): creates the virtual environment on the
REM first run, installs the dependencies and opens the dashboard in the browser.
cd /d "%~dp0"

set "PY="
py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1 && set "PY=py -3"
if not defined PY (
  python -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo ERROR: se requiere Python 3.11 o superior. Descargalo desde https://www.python.org/downloads/
  exit /b 1
)

if not exist .venv\Scripts\python.exe (
  echo ^>^> Creando entorno virtual...
  %PY% -m venv .venv || exit /b 1
)

if not exist .venv\.deps-ok (
  echo ^>^> Instalando dependencias (solo la primera vez^)...
  .venv\Scripts\python.exe -m pip install --quiet --upgrade pip
  .venv\Scripts\python.exe -m pip install --quiet -r requirements.txt || exit /b 1
  echo ok> .venv\.deps-ok
)

echo ^>^> Abriendo el dashboard en http://localhost:8501  (Ctrl+C para detenerlo^)
.venv\Scripts\python.exe -m streamlit run dashboard\app.py --server.headless false
