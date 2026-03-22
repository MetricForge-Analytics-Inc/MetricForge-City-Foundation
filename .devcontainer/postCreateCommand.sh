# ── Python dependencies ──────────────────────────────────────────────
pip install 'sqlmesh[duckdb,dlt,web,postgres,lsp]',  'dlt[motherduck,parquet]', prefect, notebook,  duckdb-async, requests

# ── Evidence (Node) ──────────────────────────────────────────────────
npm install --prefix ./Foundry-Visualization

# ── Git hooks ────────────────────────────────────────────────────────
git config core.hooksPath .githooks
