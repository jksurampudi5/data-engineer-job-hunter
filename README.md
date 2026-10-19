# 🏹 Data Engineer Job Hunter

[![CI - Test Suite](https://img.shields.io/badge/pytest-passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated, privacy-conscious Data Engineering pipeline designed to ingest, normalize, score, and track job opportunities based on specialized tech stacks (PySpark, Databricks, SQL, Apache Airflow, dbt, Kafka, Delta Lake, Snowflake, and Cloud Platforms).

---

## 🌟 Key Features

* **Multi-Format Ingestion**: Ingests job records from JSON feeds, CSV exports, and mock API endpoints.
* **Smart Deduplication**: Computes SHA-256 content fingerprints and composite business keys (`title + company + location`) to prevent duplicate applications.
* **Data Engineering Skill Matcher**: Evaluates candidates against complex DE requirements with weighted scoring for lakehouse, streaming, and cloud technologies.
* **Local Storage & Pipeline Isolation**: Stores matched opportunities and application lifecycle statuses in an isolated local SQLite/DuckDB database.
* **Automated Markdown Reporting**: Generates job matching leaderboards and skill gap analysis reports.
* **Strict Privacy Guardrails**: Engineered to exclude personal resumes, contact information, credentials, and live application history. Uses fictional sample data for public sharing.

---

## 🏗️ Architecture

```
                               ┌───────────────────────────┐
                               │  Fictional Sample Feeds   │
                               │        (JSON / CSV)       │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   JobIngestionEngine      │
                               │ (Schema Validation & Dedup)│
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       SkillMatcher        │
                               │ (DE Synonym & Weighted)   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       JobRepository       │
                               │  (Local SQLite Storage)   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │      ReportGenerator      │
                               │   (Markdown / JSON / CLI) │
                               └───────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and set up a Python virtual environment:

```bash
git clone https://github.com/jksurampudi5/data-engineer-job-hunter.git
cd data-engineer-job-hunter

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Pipeline

Run the CLI using the included fictional sample dataset:

```bash
# Run with in-memory database and view top matching jobs
python3 -m src.job_hunter.cli --input data/sample/fictional_sample_jobs.json --top 5

# Generate a formatted Markdown match report
python3 -m src.job_hunter.cli --input data/sample/fictional_sample_jobs.json --report
```

### 3. Run Tests

Verify the full pipeline test suite:

```bash
pytest -v
```

---

## 📂 Repository Structure

```
data-engineer-job-hunter/
├── .gitignore                      # Strict exclusions for resumes, credentials, and databases
├── README.md                       # Project documentation
├── requirements.txt                # Project dependencies
├── setup.py                        # Package distribution configuration
├── pytest.ini                      # Test runner configuration
├── data/
│   └── sample/
│       └── fictional_sample_jobs.json # Sanitized fictional DE jobs
├── src/
│   └── job_hunter/
│       ├── __init__.py             # Package exports
│       ├── cli.py                  # Command-line interface
│       ├── ingestion.py            # Ingestion & deduplication engine
│       ├── matcher.py              # Skill weighting & scoring engine
│       ├── models.py               # Data models & Enums
│       ├── pipeline.py             # Pipeline orchestrator
│       ├── reporter.py             # Markdown report generator
│       └── storage.py              # SQLite storage repository
└── tests/
    ├── test_cli.py                 # CLI integration tests
    ├── test_ingestion.py           # Ingestion and schema tests
    ├── test_matcher.py             # Matcher & scoring tests
    ├── test_models.py              # Data model & fingerprint tests
    └── test_pipeline.py            # End-to-end pipeline & storage tests
```

---

## 🔒 Privacy & Open-Source Security

* This repository is configured to **strictly exclude** personal resumes (`.pdf`, `.docx`), phone numbers, email addresses, `.env` files, API keys, and local SQLite databases (`*.db`, `*.sqlite`).
* All included datasets are **synthetic and fictional**.
* Intended for demonstration of Data Engineering pipeline design, testing, and portfolio display.