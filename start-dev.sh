#!/usr/bin/env bash
# =============================================================================
# Trace AI — local development startup script
#
# Starts the FastAPI backend and the Next.js frontend in parallel.
#
# Prerequisites
#   • Python 3.11+ with dependencies installed:
#       pip install -r requirements.txt
#   • Node.js 18+ with dependencies installed:
#       cd "Front End" && npm install
#
# Usage
#   bash start-dev.sh
# =============================================================================

set -euo pipefail

# Resolve the directory containing this script
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${CYAN}Starting Trace AI local development stack...${RESET}"
echo ""
echo "  Backend  →  http://localhost:8000"
echo "  Frontend →  http://localhost:3000"
echo "  API docs →  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

cleanup() {
  echo ""
  echo -e "${CYAN}Shutting down...${RESET}"
  kill 0
}
trap cleanup INT TERM

# Start backend
(
  cd "$REPO_ROOT"
  echo -e "${GREEN}[backend]${RESET} Starting FastAPI on :8000 ..."
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) &

# Start frontend
(
  cd "$REPO_ROOT/Front End"
  echo -e "${GREEN}[frontend]${RESET} Starting Next.js on :3000 ..."
  npm run dev
) &

wait
