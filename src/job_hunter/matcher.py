"""
Skill matcher and scoring engine for Data Engineering roles.
"""

import re
from typing import List, Set, Tuple
from .models import JobPosting, ProfilePreferences, MatchScore


class SkillMatcher:
    # Common alias normalization map for DE ecosystem
    SYNONYM_MAP = {
        "pyspark": "pyspark",
        "spark": "pyspark",
        "apache spark": "pyspark",
        "airflow": "apache airflow",
        "apache airflow": "apache airflow",
        "databricks": "databricks",
        "delta lake": "delta lake",
        "deltalake": "delta lake",
        "snowflake": "snowflake",
        "bigquery": "bigquery",
        "gcp": "gcp",
        "google cloud": "gcp",
        "google cloud platform": "gcp",
        "aws": "aws",
        "amazon web services": "aws",
        "dbt": "dbt",
        "kafka": "kafka",
        "apache kafka": "kafka",
        "sql": "sql",
        "python": "python",
    }

    def __init__(self, preferences: ProfilePreferences = None):
        self.preferences = preferences or ProfilePreferences()

    def normalize_skill(self, skill: str) -> str:
        s = skill.strip().lower()
        return self.SYNONYM_MAP.get(s, s)

    def extract_skills_from_text(self, text: str) -> Set[str]:
        found = set()
        lowered = text.lower()
        for alias, canonical in self.SYNONYM_MAP.items():
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, lowered):
                found.add(canonical)
        return found

    def evaluate_job(self, job: JobPosting) -> MatchScore:
        # Collect skills from explicit list + extracted from description
        job_skills = set()
        for s in job.skills:
            job_skills.add(self.normalize_skill(s))

        extracted_from_desc = self.extract_skills_from_text(job.description + " " + job.title)
        combined_job_skills = job_skills.union(extracted_from_desc)

        profile_skills = {self.normalize_skill(s) for s in self.preferences.target_skills}
        matched = combined_job_skills.intersection(profile_skills)
        missing = profile_skills.difference(combined_job_skills)

        # Weighted score calculation based on target skills
        target_canonical = {self.normalize_skill(s) for s in self.preferences.target_skills}
        total_weight = 0.0
        earned_weight = 0.0

        for skill in target_canonical:
            weight = self.preferences.skill_weights.get(skill, 1.0)
            total_weight += weight
            if skill in matched:
                earned_weight += weight

        skill_score = (earned_weight / total_weight * 70.0) if total_weight > 0 else 0.0

        # Experience fit evaluation (15 points max)
        exp_fit = job.experience_min <= self.preferences.min_years_experience <= job.experience_max
        exp_score = 15.0 if exp_fit else 5.0

        # Location fit evaluation (15 points max)
        job_loc_lower = job.location.lower()
        loc_fit = any(loc.lower() in job_loc_lower for loc in self.preferences.preferred_locations)
        if "remote" in job_loc_lower:
            loc_fit = True
        loc_score = 15.0 if loc_fit else 5.0

        overall_score = round(min(100.0, skill_score + exp_score + loc_score), 2)

        return MatchScore(
            job_id=job.job_id,
            overall_score=overall_score,
            matched_skills=sorted(list(matched)),
            missing_skills=sorted(list(missing)),
            experience_fit=exp_fit,
            location_fit=loc_fit,
            details={
                "skill_score": round(skill_score, 2),
                "exp_score": exp_score,
                "loc_score": loc_score,
                "total_skills_detected": len(combined_job_skills),
            }
        )
