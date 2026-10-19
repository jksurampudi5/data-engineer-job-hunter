import pytest
import json
import tempfile
from pathlib import Path
from src.job_hunter.ingestion import JobIngestionEngine


def test_ingestion_from_json():
    sample_data = [
        {
            "job_id": "TEST-1",
            "title": "Lead Data Engineer",
            "company": "Alpha Corp",
            "location": "Remote",
            "skills": ["PySpark", "Databricks"],
            "experience_min": 4,
            "experience_max": 8,
        },
        {
            # Duplicate job content to verify deduplication
            "job_id": "TEST-2",
            "title": "Lead Data Engineer",
            "company": "Alpha Corp",
            "location": "Remote",
            "skills": ["PySpark", "Databricks"],
        }
    ]

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(sample_data, f)
        temp_path = f.name

    try:
        engine = JobIngestionEngine()
        jobs = engine.load_from_json(temp_path)
        # Deduplication should ensure only 1 job is kept
        assert len(jobs) == 1
        assert jobs[0].job_id == "TEST-1"
        assert jobs[0].company == "Alpha Corp"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_ingestion_file_not_found():
    engine = JobIngestionEngine()
    with pytest.raises(FileNotFoundError):
        engine.load_from_json("non_existent_file.json")


def test_ingestion_real_jobs_file():
    real_jobs_path = Path(__file__).parent.parent / "data" / "jobs.json"
    assert real_jobs_path.exists()
    engine = JobIngestionEngine()
    jobs = engine.load_from_json(real_jobs_path)
    assert len(jobs) >= 20
    assert any("Amazon" in j.company for j in jobs)
    assert all(bool(j.application_url) for j in jobs)

