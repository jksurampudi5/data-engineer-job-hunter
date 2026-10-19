import pytest
from src.job_hunter.models import JobPosting, ProfilePreferences, MatchScore, ApplicationStatus


def test_job_posting_serialization():
    job = JobPosting(
        job_id="TEST-001",
        title="Senior Data Engineer",
        company="MockCorp",
        location="Remote",
        skills=["Python", "PySpark", "SQL"],
        experience_min=3,
        experience_max=6,
        status=ApplicationStatus.DISCOVERED,
    )

    data = job.to_dict()
    assert data["job_id"] == "TEST-001"
    assert data["status"] == "DISCOVERED"
    assert len(data["skills"]) == 3

    reconstructed = JobPosting.from_dict(data)
    assert reconstructed.job_id == job.job_id
    assert reconstructed.status == ApplicationStatus.DISCOVERED


def test_job_fingerprint_generation():
    job1 = JobPosting(
        job_id="A",
        title="Data Engineer",
        company="TechCorp",
        location="Bangalore",
    )
    job2 = JobPosting(
        job_id="B",
        title="  data engineer  ",
        company="TECHCORP",
        location="bangalore",
    )
    assert job1.generate_fingerprint() == job2.generate_fingerprint()
