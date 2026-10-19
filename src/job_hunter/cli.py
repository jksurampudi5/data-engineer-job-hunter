"""
Command-line interface for the Data Engineer Job Hunter pipeline.
"""

import argparse
import sys
from pathlib import Path
from .pipeline import JobHunterPipeline
from .reporter import ReportGenerator


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Data Engineer Job Hunter: Ingestion, Scoring, and Opportunity Tracker"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(Path(__file__).parent.parent.parent / "data" / "sample" / "fictional_sample_jobs.json"),
        help="Path to JSON or CSV file containing job postings",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=":memory:",
        help="Path to SQLite database file (defaults to in-memory)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print full markdown matching report to stdout",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top matching jobs to display",
    )

    parsed = parser.parse_args(args)

    print(f"🚀 Initializing Data Engineer Job Hunter Pipeline...")
    print(f"📁 Source: {parsed.input}")
    print(f"💾 Storage: {parsed.db}")

    pipeline = JobHunterPipeline(db_path=parsed.db)
    result = pipeline.run_pipeline(parsed.input)

    print("\n✅ Pipeline Execution Completed:")
    print(f"  • Total Jobs Ingested: {result['total_ingested']}")
    print(f"  • Total Jobs Scored:   {result['total_scored']}")
    print(f"  • Average Match Score: {result['avg_score']}%")
    print(f"  • High Matches (>=70%): {result['top_match_count']}")

    print("\n🏆 Top Matches:")
    for idx, match in enumerate(result["top_matches"][:parsed.top], start=1):
        print(f"  {idx}. [{match['score']}%] {match['title']} @ {match['company']} ({match['location']})")
        print(f"     Matched: {', '.join(match['matched_skills'])}")

    if parsed.report:
        report_md = ReportGenerator.generate_markdown_report(result)
        print("\n" + "=" * 50)
        print(report_md)
        print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
