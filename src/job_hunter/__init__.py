"""
Data Engineer Job Hunter
Automated pipeline for discovering, matching, scoring, and tracking Data Engineering opportunities.
"""

__version__ = "1.0.0"
__author__ = "Data Engineer Job Hunter Contributors"

from .models import JobPosting, ProfilePreferences, MatchScore, ApplicationStatus
from .ingestion import JobIngestionEngine
from .matcher import SkillMatcher
from .storage import JobRepository
from .pipeline import JobHunterPipeline
from .reporter import ReportGenerator

__all__ = [
    "JobPosting",
    "ProfilePreferences",
    "MatchScore",
    "ApplicationStatus",
    "JobIngestionEngine",
    "SkillMatcher",
    "JobRepository",
    "JobHunterPipeline",
    "ReportGenerator",
]
