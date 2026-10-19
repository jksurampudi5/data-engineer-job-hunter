import pytest
from pathlib import Path
from src.job_hunter.pipeline import JobHunterPipeline
from src.job_hunter.storage import JobRepository
from src.job_hunter.models import ApplicationStatus


def test_pipeline_end_to_end():
    sample_file = Path(__file__).parent.parent / "data" / "sample" / "fictional_sample_jobs.json"
    assert sample_file.exists(), f"Sample data file missing: {sample_file}"

    pipeline = JobHunterPipeline(db_path=":memory:")
    result = pipeline.run_pipeline(str(sample_file))

    assert result["total_ingested"] >= 5
    assert result["total_scored"] >= 5
    assert len(result["top_matches"]) > 0
    assert result["avg_score"] > 0

    # Top match should have a high score
    top = result["top_matches"][0]
    assert top["score"] >= 60.0
    assert "job_id" in top
    assert "title" in top


def test_repository_status_update():
    repo = JobRepository(":memory:")
    sample_file = Path(__file__).parent.parent / "data" / "sample" / "fictional_sample_jobs.json"
    pipeline = JobHunterPipeline(db_path=":memory:")
    pipeline.run_pipeline(str(sample_file))

    # Test status transition
    updated = pipeline.repository.update_status("DE-SAMPLE-101", ApplicationStatus.REVIEWED)
    assert updated is True
