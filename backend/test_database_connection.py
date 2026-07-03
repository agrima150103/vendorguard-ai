"""
Quick database connectivity test for VendorGuard.

Run from the backend folder:

    python test_database_connection.py
"""

from __future__ import annotations

import traceback

from sqlalchemy import text

from app.config import settings
from app.repositories.assessment_repository import (
    engine,
    init_db,
    list_assessments,
)


def main() -> int:
    print("VendorGuard database connectivity test")
    print("--------------------------------------")

    print(
        "Database URL type:",
        "PostgreSQL"
        if settings.using_postgres
        else "SQLite",
    )

    print(
        "Database URL:",
        settings.sqlalchemy_database_url,
    )

    print(
        "Sample data path:",
        settings.resolved_sample_data_path,
    )

    print(
        "Sample data exists:",
        settings.resolved_sample_data_path.exists(),
    )

    print()
    print("Initialising database...")
    init_db()

    print("Running SELECT 1...")

    with engine.connect() as connection:
        value = connection.execute(
            text("select 1"),
        ).scalar_one()

    print("SELECT 1:", value)

    assessments = list_assessments()

    print("Assessments:", len(assessments))

    print()
    print("SUCCESS: database connection works")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print()
        print("FAILED: database connection test crashed")
        traceback.print_exc()
        raise SystemExit(1)