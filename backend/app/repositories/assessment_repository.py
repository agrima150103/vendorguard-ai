from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import settings
from app.models.schemas import Assessment, AssessmentSummary


class AssessmentRepositoryError(RuntimeError):
    pass


def _db_path() -> Path:
    path = Path(settings.db_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_db_path(), timeout=10, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    return connection


def init_db() -> None:
    try:
        with get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id TEXT PRIMARY KEY,
                    vendor_id TEXT NOT NULL,
                    vendor_name TEXT NOT NULL,
                    risk_tier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    recommendation TEXT,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
    except sqlite3.Error as exc:
        raise AssessmentRepositoryError(str(exc)) from exc


def save_assessment(assessment: Assessment) -> None:
    recommendation = assessment.recommendation.decision.value if assessment.recommendation else None
    try:
        with get_connection() as connection:
            connection.execute("""
                INSERT INTO assessments (
                    assessment_id, vendor_id, vendor_name, risk_tier, status,
                    recommendation, data, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(assessment_id) DO UPDATE SET
                    status=excluded.status,
                    recommendation=excluded.recommendation,
                    data=excluded.data,
                    updated_at=excluded.updated_at
            """, (
                assessment.assessment_id,
                assessment.vendor_id,
                assessment.vendor_name,
                assessment.risk_tier.value,
                assessment.status.value,
                recommendation,
                assessment.model_dump_json(),
                assessment.created_at.isoformat(),
                assessment.updated_at.isoformat(),
            ))
    except sqlite3.Error as exc:
        raise AssessmentRepositoryError(str(exc)) from exc


def get_assessment(assessment_id: str) -> Assessment | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT data FROM assessments WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchone()
    return Assessment.model_validate_json(row["data"]) if row else None


def list_assessments() -> list[AssessmentSummary]:
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT assessment_id, vendor_id, vendor_name, risk_tier, status,
                   recommendation, created_at, updated_at
            FROM assessments ORDER BY created_at DESC
        """).fetchall()
    return [AssessmentSummary.model_validate(dict(row)) for row in rows]
