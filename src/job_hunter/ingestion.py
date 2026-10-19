"""
Job ingestion engine for loading, validating, and deduplicating job postings.
"""

import json
import csv
from typing import List, Dict, Any, Union
from pathlib import Path
from datetime import datetime
from .models import JobPosting, ApplicationStatus


class JobIngestionEngine:
    def __init__(self):
        self.seen_fingerprints = set()

    def load_from_json(self, file_path: Union[str, Path]) -> List[JobPosting]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("Expected a JSON list of job postings")

        return self.process_raw_records(raw_data)

    def load_from_csv(self, file_path: Union[str, Path]) -> List[JobPosting]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        records = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse skills list if comma-separated
                skills_raw = row.get("skills", "")
                skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
                row["skills"] = skills
                if "experience_min" in row and row["experience_min"]:
                    row["experience_min"] = int(row["experience_min"])
                if "experience_max" in row and row["experience_max"]:
                    row["experience_max"] = int(row["experience_max"])
                records.append(row)

        return self.process_raw_records(records)

    def process_raw_records(self, raw_records: List[Dict[str, Any]]) -> List[JobPosting]:
        valid_postings: List[JobPosting] = []

        for idx, item in enumerate(raw_records):
            job_id = str(item.get("job_id") or f"JOB-AUTO-{idx+1}")
            title = str(item.get("title", "Untitled Role")).strip()
            company = str(item.get("company", "Confidential")).strip()
            location = str(item.get("location", "Not Specified")).strip()
            source = str(item.get("source", "Standard Intake")).strip()
            exp_min = int(item.get("experience_min", 0))
            exp_max = int(item.get("experience_max", 10))
            skills = item.get("skills", [])
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
            description = str(item.get("description", "")).strip()
            salary = str(item.get("salary_range", "Not Disclosed")).strip()
            posted_date = str(item.get("posted_date") or datetime.now().strftime("%Y-%m-%d"))

            posting = JobPosting(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                source=source,
                experience_min=exp_min,
                experience_max=exp_max,
                skills=skills,
                description=description,
                salary_range=salary,
                posted_date=posted_date,
                status=ApplicationStatus.DISCOVERED,
                created_at=datetime.utcnow().isoformat(),
            )

            # Deduplication check
            fingerprint = posting.generate_fingerprint()
            if fingerprint in self.seen_fingerprints:
                continue

            self.seen_fingerprints.add(fingerprint)
            valid_postings.append(posting)

        return valid_postings
