import argparse
import subprocess
import sys
from pathlib import Path

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
def extract(vendor: str) -> None:
    """Run the DLT extract pipeline for the given vendor."""
    root = _workspace_root()
    script = root / "Foundry-Pipelines" / "Support" / vendor / "Data-Extract" / f"{vendor}_pipeline.py"
    _run(f"{sys.executable} {script}", cwd=root)


@task(name="sqlmesh-transform")
def transform(vendor: str) -> None:
    """Run SQLMesh plan against prod with auto-apply."""
    root = _workspace_root()
    extract_path = root / "Foundry-Pipelines" / "Support" / vendor / "Data-Extract"
    pipeline_path = root / "Foundry-Pipelines" / "Support" / vendor / "Data-Pipeline"
    log_dir = root / "Foundry-Orchestration" / "logs"
    _run(
        f"sqlmesh --log-file-dir {log_dir}"
        f" -p {extract_path} -p {pipeline_path}"
        f" plan prod --auto-apply --no-prompts --skip-tests",
        cwd=root,
    )


@flow(name="support-pipeline")
def main() -> None:
    parser = argparse.ArgumentParser(description="MetricForge Support Pipeline")
    parser.add_argument("--vendor", default="zendesk", help="Data vendor to run")
    args = parser.parse_args()

    extract(args.vendor)
    transform(args.vendor)


if __name__ == "__main__":
    main()

