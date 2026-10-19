import pytest
from pathlib import Path
from src.job_hunter.cli import main


def test_cli_execution():
    sample_file = str(Path(__file__).parent.parent / "data" / "sample" / "fictional_sample_jobs.json")
    exit_code = main(["--input", sample_file, "--top", "3", "--report"])
    assert exit_code == 0
