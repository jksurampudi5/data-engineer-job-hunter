import pytest
from src.job_hunter.models import JobPosting, ProfilePreferences
from src.job_hunter.matcher import SkillMatcher


def test_skill_matcher_scoring():
    prefs = ProfilePreferences(
        target_skills=["Python", "PySpark", "Databricks", "SQL"],
        min_years_experience=3,
        preferred_locations=["Hyderabad", "Remote"],
    )
    matcher = SkillMatcher(preferences=prefs)

    job = JobPosting(
        job_id="TEST-DE-1",
        title="PySpark Databricks Developer",
        company="DataCloud",
        location="Hyderabad",
        skills=["Python", "PySpark", "Databricks", "SQL"],
        experience_min=2,
        experience_max=5,
        description="Build large-scale Spark jobs on Databricks with SQL optimization.",
    )

    score = matcher.evaluate_job(job)
    assert score.overall_score >= 80.0
    assert score.experience_fit is True
    assert score.location_fit is True
    assert "pyspark" in score.matched_skills
    assert "databricks" in score.matched_skills


def test_skill_normalization_synonyms():
    matcher = SkillMatcher()
    assert matcher.normalize_skill("Apache Spark") == "pyspark"
    assert matcher.normalize_skill("delta lake") == "delta lake"
    assert matcher.normalize_skill("Google Cloud Platform") == "gcp"
