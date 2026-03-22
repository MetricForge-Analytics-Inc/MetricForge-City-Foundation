import argparse
import subprocess
import sys
from pathlib import Path

import requests
from prefect import flow, task, get_run_logger


def _workspace_root() -> Path:
    """Resolve the workspace root (parent of Foundry-Orchestration/)."""
    return Path(__file__).resolve().parent.parent


def _run(cmd: str, cwd: Path | None = None) -> None:
    """Run a shell command, raising on failure."""
    logger = get_run_logger()
    logger.info("Running: %s", cmd)
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    result.check_returncode()


@task(name="dlt-extract")
def extract(theme: str, site: str) -> None:
    """Run the DLT extract pipeline for the given theme/site."""
    root = _workspace_root()
    # Convention: pipeline script is named {site_snake}_pipeline.py
    site_snake = site.lower().replace("-", "_")
    script = (
        root / "Foundry-Pipelines" / theme / site
        / "Data-Extract" / f"{site_snake}_pipeline.py"
    )
    if not script.exists():
        # Fallback: look for opendata_pipeline.py (Kitchener open data)
        script = root / "Foundry-Pipelines" / theme / site / "Data-Extract" / "opendata_pipeline.py"
    _run(f"{sys.executable} {script}", cwd=script.parent)


@task(name="sqlmesh-transform")
def transform(theme: str, site: str) -> None:
    """Run SQLMesh plan against the local environment with auto-apply."""
    root = _workspace_root()
    pipeline_path = root / "Foundry-Pipelines" / theme / site / "Data-Pipeline"
    log_dir = root / "Foundry-Orchestration" / "logs"
    _run(
        f"sqlmesh --log-file-dir {log_dir}"
        f" plan local --auto-apply --no-prompts --skip-tests",
        cwd=pipeline_path,
    )


CUBE_API_URL = "http://localhost:4000/cubejs-api/v1"
CUBE_API_SECRET = "metricforge-local-dev-secret"


@task(name="cube-refresh")
def refresh_cube() -> None:
    """Tell the local Cube.js instance to reload its schema cache.

    This is a best-effort step — if Cube isn't running, we skip gracefully
    so the pipeline still completes.
    """
    logger = get_run_logger()
    headers = {"Authorization": CUBE_API_SECRET}
    try:
        resp = requests.get(
            f"{CUBE_API_URL}/meta",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        cubes = resp.json().get("cubes", [])
        logger.info("Cube.js reachable — %d cube(s) loaded: %s",
                     len(cubes), [c["name"] for c in cubes])
    except requests.ConnectionError:
        logger.info("Cube.js not running — skipping semantic refresh")
    except Exception as exc:
        logger.warning("Cube.js refresh check failed: %s", exc)


@flow(name="city-pipeline")
def main() -> None:
    parser = argparse.ArgumentParser(description="MetricForge City Foundation Pipeline")
    parser.add_argument(
        "--theme", default="Infrastructure",
        help="Pipeline theme folder (e.g. Infrastructure, PublicHealth)",
    )
    parser.add_argument(
        "--site", default="OpenData-Kitchener",
        help="Site/source within the theme (e.g. OpenData-Kitchener)",
    )
    args = parser.parse_args()

    extract(args.theme, args.site)
    transform(args.theme, args.site)
    refresh_cube()


if __name__ == "__main__":
    main()
