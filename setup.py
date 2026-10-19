from setuptools import setup, find_packages

setup(
    name="data-engineer-job-hunter",
    version="1.0.0",
    description="Automated Data Engineer job hunting, scoring, and pipeline tracker",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "job-hunter=src.job_hunter.cli:main",
        ],
    },
)
