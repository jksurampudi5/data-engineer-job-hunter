"""
Report generation module for formatting job opportunities and skills gap analysis.
"""

from typing import List, Dict, Any
from datetime import datetime


class ReportGenerator:
    @staticmethod
    def generate_markdown_report(pipeline_result: Dict[str, Any]) -> str:
        top_matches = pipeline_result.get("top_matches", [])
        total_ingested = pipeline_result.get("total_ingested", 0)
        avg_score = pipeline_result.get("avg_score", 0.0)

        lines = [
            "# 📊 Data Engineer Job Match Report",
            f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Ingested**: {total_ingested} | **Average Match Score**: {avg_score}%",
            "",
            "## 🎯 Top Matched Opportunities",
            "",
            "| Rank | Job ID | Title | Company | Location | Score | Key Matched Skills |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for idx, job in enumerate(top_matches, start=1):
            matched_skills_str = ", ".join(job["matched_skills"]) if job["matched_skills"] else "None"
            lines.append(
                f"| #{idx} | `{job['job_id']}` | **{job['title']}** | {job['company']} | {job['location']} | `{job['score']}%` | {matched_skills_str} |"
            )

        lines.extend([
            "",
            "## 💡 Skills Breakdown & Observations",
            "- Lakehouse architectures (PySpark, Databricks, Delta Lake) demonstrate high alignment.",
            "- Cloud integrations (Airflow + GCP/AWS) remain frequent requirements.",
            "",
            "> *Note: Generated using fictional sample data in automated test mode.*",
        ])

        return "\n".join(lines)
