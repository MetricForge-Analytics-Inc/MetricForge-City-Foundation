# ─────────────────────────────────────────────────────────────────
#  Cube.js Local Configuration
#  Runs against the local DuckDB file produced by the pipeline.
#  Model files live in City/ (mapped as /cube/conf/model in Docker).
# ─────────────────────────────────────────────────────────────────
from cube import config

@config('scheduled_refresh_contexts')
def scheduled_refresh_contexts() -> list:
    return [{'securityContext': {}}]
