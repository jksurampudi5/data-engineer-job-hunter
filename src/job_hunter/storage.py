"""
SQLite storage repository for job postings and matching evaluation results.
"""

import sqlite3
import json
from typing import List, Optional, Tuple, Dict, Any
from .models import JobPosting, MatchScore, ApplicationStatus


class JobRepository:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
            self._conn.row_factory = sqlite3.Row
        else:
            self._conn = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    source TEXT,
                    experience_min INTEGER,
                    experience_max INTEGER,
                    skills_json TEXT,
                    description TEXT,
                    salary_range TEXT,
                    posted_date TEXT,
                    status TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    job_id TEXT PRIMARY KEY,
                    overall_score REAL NOT NULL,
                    matched_skills_json TEXT,
                    missing_skills_json TEXT,
                    experience_fit INTEGER,
                    location_fit INTEGER,
                    details_json TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            """)
            conn.commit()

    def upsert_job(self, job: JobPosting) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (
                    job_id, title, company, location, source, experience_min, experience_max,
                    skills_json, description, salary_range, posted_date, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    title=excluded.title,
                    company=excluded.company,
                    location=excluded.location,
                    skills_json=excluded.skills_json,
                    description=excluded.description,
                    salary_range=excluded.salary_range,
                    status=excluded.status
            """, (
                job.job_id, job.title, job.company, job.location, job.source,
                job.experience_min, job.experience_max, json.dumps(job.skills),
                job.description, job.salary_range, job.posted_date, job.status.value,
                job.created_at
            ))
            conn.commit()

    def save_evaluation(self, score: MatchScore) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluations (
                    job_id, overall_score, matched_skills_json, missing_skills_json,
                    experience_fit, location_fit, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    overall_score=excluded.overall_score,
                    matched_skills_json=excluded.matched_skills_json,
                    missing_skills_json=excluded.missing_skills_json,
                    experience_fit=excluded.experience_fit,
                    location_fit=excluded.location_fit,
                    details_json=excluded.details_json
            """, (
                score.job_id, score.overall_score, json.dumps(score.matched_skills),
                json.dumps(score.missing_skills), 1 if score.experience_fit else 0,
                1 if score.location_fit else 0, json.dumps(score.details)
            ))
            conn.commit()

    def get_top_matches(self, limit: int = 10, min_score: float = 0.0) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    j.job_id, j.title, j.company, j.location, j.salary_range, j.status,
                    e.overall_score, e.matched_skills_json, e.missing_skills_json,
                    e.experience_fit, e.location_fit
                FROM jobs j
                JOIN evaluations e ON j.job_id = e.job_id
                WHERE e.overall_score >= ?
                ORDER BY e.overall_score DESC
                LIMIT ?
            """, (min_score, limit))
            rows = cursor.fetchall()

            results = []
            for r in rows:
                results.append({
                    "job_id": r["job_id"],
                    "title": r["title"],
                    "company": r["company"],
                    "location": r["location"],
                    "salary_range": r["salary_range"],
                    "status": r["status"],
                    "score": r["overall_score"],
                    "matched_skills": json.loads(r["matched_skills_json"]),
                    "missing_skills": json.loads(r["missing_skills_json"]),
                    "exp_fit": bool(r["experience_fit"]),
                    "loc_fit": bool(r["location_fit"]),
                })
            return results

    def update_status(self, job_id: str, new_status: ApplicationStatus) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (new_status.value, job_id))
            conn.commit()
            return cursor.rowcount > 0
