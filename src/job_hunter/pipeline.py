"""
Orchestration pipeline connecting ingestion, scoring, and storage.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .models import JobPosting, ProfilePreferences, MatchScore, ApplicationStatus
from .ingestion import JobIngestionEngine
from .matcher import SkillMatcher
from .storage import JobRepository


class JobHunterPipeline:
    def __init__(self, db_path: str = ":memory:", preferences: Optional[ProfilePreferences] = None):
        self.repository = JobRepository(db_path)
        self.preferences = preferences or ProfilePreferences()
        self.ingestion_engine = JobIngestionEngine()
        self.matcher = SkillMatcher(self.preferences)

    def run_pipeline(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        if path.suffix.lower() == ".json":
            jobs = self.ingestion_engine.load_from_json(path)
        elif path.suffix.lower() == ".csv":
            jobs = self.ingestion_engine.load_from_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        scores: List[MatchScore] = []
        for job in jobs:
            score = self.matcher.evaluate_job(job)
            if score.overall_score >= 60.0:
                job.status = ApplicationStatus.MATCHED
            self.repository.upsert_job(job)
            self.repository.save_evaluation(score)
            scores.append(score)

        scores_sorted = sorted(scores, key=lambda s: s.overall_score, reverse=True)
        top_matches = self.repository.get_top_matches(limit=5)

        return {
            "total_ingested": len(jobs),
            "total_scored": len(scores),
            "avg_score": round(sum(s.overall_score for s in scores) / len(scores), 2) if scores else 0.0,
            "top_match_count": len([s for s in scores if s.overall_score >= 70.0]),
            "top_matches": top_matches,
        }
