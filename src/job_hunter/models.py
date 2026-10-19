"""
Data models for the Data Engineer Job Hunter pipeline.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import hashlib
import json


class ApplicationStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    MATCHED = "MATCHED"
    REVIEWED = "REVIEWED"
    APPLIED = "APPLIED"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    ARCHIVED = "ARCHIVED"


@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    location: str
    source: str = "Unknown"
    experience_min: int = 0
    experience_max: int = 10
    skills: List[str] = field(default_factory=list)
    description: str = ""
    salary_range: str = "Not Disclosed"
    posted_date: str = ""
    application_url: str = ""
    status: ApplicationStatus = ApplicationStatus.DISCOVERED
    created_at: str = ""

    def generate_fingerprint(self) -> str:
        """Create a deterministic SHA-256 fingerprint for deduplication."""
        normalized = f"{self.title.strip().lower()}|{self.company.strip().lower()}|{self.location.strip().lower()}"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobPosting":
        payload = data.copy()
        if "status" in payload and isinstance(payload["status"], str):
            payload["status"] = ApplicationStatus(payload["status"])
        return cls(**payload)


@dataclass
class ProfilePreferences:
    target_role: str = "Data Engineer"
    target_skills: List[str] = field(default_factory=lambda: [
        "Python", "PySpark", "SQL", "Databricks", "Apache Spark", "Apache Airflow", "dbt", "Delta Lake"
    ])
    preferred_locations: List[str] = field(default_factory=lambda: ["Remote", "Bangalore", "Hyderabad", "Pune"])
    min_years_experience: int = 3
    skill_weights: Dict[str, float] = field(default_factory=lambda: {
        "pyspark": 2.5,
        "databricks": 2.0,
        "sql": 2.0,
        "python": 2.0,
        "apache airflow": 1.5,
        "delta lake": 1.5,
        "dbt": 1.5,
        "kafka": 1.2,
        "snowflake": 1.2,
        "bigquery": 1.2,
        "aws": 1.0,
        "gcp": 1.0,
    })


@dataclass
class MatchScore:
    job_id: str
    overall_score: float  # 0 to 100
    matched_skills: List[str]
    missing_skills: List[str]
    experience_fit: bool
    location_fit: bool
    details: Dict[str, Any] = field(default_factory=dict)
