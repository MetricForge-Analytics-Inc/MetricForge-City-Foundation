#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# ── Colors ───────────────────────────────────────────────────────────
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() { echo -e "\n${CYAN}==> $1${NC}"; }
ok()   { echo -e "${GREEN}    ✓ $1${NC}"; }
warn() { echo -e "${YELLOW}    ! $1${NC}"; }

# ── Load .env ────────────────────────────────────────────────────────
if [ -f .env ]; then
  set -a
  source .env
  set +a
  ok "Loaded .env"
fi

# ── 1. Python venv ──────────────────────────────────────────────────
step "Setting up Python venv"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ok "Created .venv"
else
  ok ".venv already exists"
fi
source .venv/bin/activate

step "Installing Python dependencies"
pip install -q -r Foundry-Orchestration/requirements.txt
ok "Python deps installed"

# ── 2. Create db directory ──────────────────────────────────────────
mkdir -p db

# ── 3. DLT Extract (pull open data into DuckDB) ────────────────────
if [ -f db/foundry.duckdb ] && [ "$(stat -f%z db/foundry.duckdb 2>/dev/null || echo 0)" -gt 100000 ]; then
  step "Skipping DLT extract (db/foundry.duckdb already has data)"
  ok "Use: rm db/foundry.duckdb to force re-extract"
else
  step "Running DLT extract → DuckDB"
  cd Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Extract
  python opendata_pipeline.py
  cd "$ROOT"
  ok "Data extracted into db/foundry.duckdb"
fi

# ── 4. SQLMesh Transform (build views) ─────────────────────────────
step "Running SQLMesh transforms"
export SQLMESH_HOME="$ROOT/.sqlmesh"
PIPELINE_PATH="$ROOT/Foundry-Pipelines/Infrastructure/OpenData-Kitchener/Data-Pipeline"
sqlmesh -p "$PIPELINE_PATH" plan prod --auto-apply --no-prompts --skip-tests
ok "SQLMesh views built"

# ── 5. Install Node deps for Evidence ──────────────────────────────
step "Installing Evidence (Node) dependencies"
cd Foundry-Visualization
npm install --silent 2>/dev/null
cd "$ROOT"
ok "Evidence deps installed"

# ── 6. Install Cube.js ─────────────────────────────────────────────
step "Installing Cube.js"
npm install --prefix Foundry-Semantic-Cubes --silent @cubejs-backend/server @cubejs-backend/duckdb-driver 2>/dev/null
ok "Cube.js installed"

# ── 7. Start Cube.js in background ─────────────────────────────────
step "Starting Cube.js (API :4000 / SQL :15432)"
cd Foundry-Semantic-Cubes
npx cubejs-server &
CUBE_PID=$!
cd "$ROOT"

# Wait for Cube SQL API to be ready
echo -n "    Waiting for Cube SQL API"
for i in $(seq 1 30); do
  if nc -z localhost 15432 2>/dev/null; then
    echo ""
    ok "Cube.js is ready"
    break
  fi
  echo -n "."
  sleep 2
done

# ── 8. Start Evidence dev server ────────────────────────────────────
step "Starting Evidence (http://localhost:3000)"
cd Foundry-Visualization
npm run sources 2>/dev/null || warn "Source pull had issues (Cube may still be warming up)"
npm run dev -- --host 0.0.0.0 --port 3000 &
EVIDENCE_PID=$!
cd "$ROOT"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  All services running!${NC}"
echo -e "${GREEN}  Evidence dashboard : http://localhost:3000${NC}"
echo -e "${GREEN}  Cube.js playground : http://localhost:4000${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Press Ctrl+C to stop everything${NC}\n"

# ── Cleanup on exit ─────────────────────────────────────────────────
cleanup() {
  echo -e "\n${CYAN}Shutting down...${NC}"
  kill $CUBE_PID 2>/dev/null
  kill $EVIDENCE_PID 2>/dev/null
  wait 2>/dev/null
  echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# Keep script alive
wait
