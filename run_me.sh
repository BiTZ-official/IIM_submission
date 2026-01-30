#!/usr/bin/env bash
# run_me.sh — universal script for Linux/macOS
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Starting program . . ."

# --- Determine Python executable ---
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo "Python not found. Install Python 3.8+ and re-run." >&2; exit 1; fi

# --- Check Python version >= 3.8 ---
$PY - <<'PY' || { echo "Python 3.8+ is required." >&2; $PY -V; exit 2; }
import sys
if sys.version_info < (3,8):
    raise SystemExit(2)
print("OK")
PY

# --- Create venv if missing ---
if [ ! -d ".venv" ]; then
  $PY -m venv .venv
fi

# --- Activate venv ---
# shellcheck source=/dev/null
. .venv/bin/activate

pip install --upgrade pip
pip install -r code-files/requirements.txt

# --- Function to open new terminal window cross-platform ---
open_terminal() {
  local cmd="$1"
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v gnome-terminal >/dev/null 2>&1; then
      gnome-terminal -- bash -c "$cmd; exec bash"
    elif command -v xterm >/dev/null 2>&1; then
      xterm -hold -e "$cmd"
    else
      echo "No supported terminal found (gnome-terminal/xterm). Running in background..."
      bash -c "$cmd" &
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$ROOT_DIR'; source .venv/bin/activate; $cmd\""
  else
    echo "Unsupported OS type: $OSTYPE"
    bash -c "$cmd" &
  fi
}

# --- Run other services in new windows ---
open_terminal "python code-files/process.py"
open_terminal "python code-files/simulated_data.py"

echo "Booting program . . ."

# --- Wait until both API ports are accepting connections ---
echo "Waiting for services to start on ports 8080 and 8090..."
t0=$(date +%s)
while ! (nc -z 127.0.0.1 8080 && nc -z 127.0.0.1 8090); do
  now=$(date +%s)
  if (( now - t0 > 30 )); then
    echo "Timeout waiting for services. Continuing anyway."
    break
  fi
  sleep 5
done
echo "Testing complete."

# --- Run main processor in current window ---
echo "Booting UI..."
python code-files/main.processor.py

# --- Keep terminal open after finishing ---
echo "Boot complete . . ."
read -rp "Press Enter to close..."
