from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import Assessment, AssessmentSummary


class AssessmentRepositoryError(RuntimeError):
    """Raised when assessment persistence fails."""


metadata = MetaData()


assessments_table = Table(
    "assessments",
    metadata,
    Column(
        "assessment_id",
        String(64),
        primary_key=True,
    ),
    Column(
        "vendor_id",
        String(128),
        nullable=False,
        index=True,
    ),
    Column(
        "vendor_name",
        String(255),
        nullable=False,
    ),
    Column(
        "risk_tier",
        String(32),
        nullable=False,
        index=True,
    ),
    Column(
        "status",
        String(64),
        nullable=False,
        index=True,
    ),
    Column(
        "recommendation",
        String(128),
        nullable=True,
    ),
    Column(
        "data",
        Text,
        nullable=False,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        index=True,
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
    ),
)


def _create_engine():
    """
    Create the SQLAlchemy engine.

    Local development uses SQLite.
    Production uses PostgreSQL/Supabase.
    """

    url = settings.sqlalchemy_database_url

    if url.startswith("sqlite"):
        return create_engine(
            url,
            future=True,
            connect_args={
                "check_same_thread": False,
            },
        )

    return create_engine(
        url,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool,
    )


engine = _create_engine()


def init_db() -> None:
    """Create assessment storage when it does not already exist."""

    try:
        metadata.create_all(engine)
    except SQLAlchemyError as exc:
        raise AssessmentRepositoryError(
            str(exc)
        ) from exc


def save_assessment(
    assessment: Assessment,
) -> None:
    """Insert or update a complete assessment JSON record."""

    recommendation = (
        assessment.recommendation.decision.value
        if assessment.recommendation
        else None
    )

    payload = {
        "assessment_id": assessment.assessment_id,
        "vendor_id": assessment.vendor_id,
        "vendor_name": assessment.vendor_name,
        "risk_tier": assessment.risk_tier.value,
        "status": assessment.status.value,
        "recommendation": recommendation,
        "data": assessment.model_dump_json(),
        "created_at": assessment.created_at,
        "updated_at": assessment.updated_at,
    }

    try:
        with engine.begin() as connection:
            existing = connection.execute(
                select(
                    assessments_table.c.assessment_id,
                ).where(
                    assessments_table.c.assessment_id
                    == assessment.assessment_id
                )
            ).first()

            if existing:
                connection.execute(
                    assessments_table.update()
                    .where(
                        assessments_table.c.assessment_id
                        == assessment.assessment_id
                    )
                    .values(
                        status=payload["status"],
                        recommendation=payload[
                            "recommendation"
                        ],
                        data=payload["data"],
                        updated_at=payload[
                            "updated_at"
                        ],
                    )
                )
            else:
                connection.execute(
                    assessments_table.insert().values(
                        **payload,
                    )
                )

    except SQLAlchemyError as exc:
        raise AssessmentRepositoryError(
            str(exc)
        ) from exc


def get_assessment(
    assessment_id: str,
) -> Assessment | None:
    """Return a saved assessment by ID."""

    try:
        with engine.connect() as connection:
            row = connection.execute(
                select(
                    assessments_table.c.data,
                ).where(
                    assessments_table.c.assessment_id
                    == assessment_id
                )
            ).first()

    except SQLAlchemyError as exc:
        raise AssessmentRepositoryError(
            str(exc)
        ) from exc

    if row is None:
        return None

    try:
        return Assessment.model_validate_json(
            row.data,
        )
    except ValidationError as exc:
        raise AssessmentRepositoryError(
            f"Saved assessment {assessment_id} could not be validated: {exc}"
        ) from exc


def _pipeline_mode(
    assessment: Assessment,
) -> str:
    """Derive pipeline mode from the assessment audit log."""

    events = {
        entry.event
        for entry in assessment.audit_log
    }

    if "ADK_PIPELINE_COMPLETE" in events:
        return "ADK"

    if "ADK_PIPELINE_FAILED" in events:
        return "FALLBACK"

    selected = next(
        (
            entry.detail.lower()
            for entry in assessment.audit_log
            if entry.event
            == "PIPELINE_SELECTED"
        ),
        "",
    )

    if "deterministic" in selected:
        return "DETERMINISTIC"

    if "fallback" in selected:
        return "FALLBACK"

    if "gemini" in selected:
        return "GEMINI"

    return "UNKNOWN"


def list_assessments() -> list[AssessmentSummary]:
    """Return assessment summaries from newest to oldest."""

    try:
        with engine.connect() as connection:
            rows = connection.execute(
                select(
                    assessments_table.c.data,
                ).order_by(
                    assessments_table.c.created_at.desc(),
                )
            ).all()

    except SQLAlchemyError as exc:
        raise AssessmentRepositoryError(
            str(exc)
        ) from exc

    summaries: list[AssessmentSummary] = []

    for row in rows:
        try:
            assessment = Assessment.model_validate_json(
                row.data,
            )
        except ValidationError:
            # Old local demo records may not match the newest schema.
            # Skip invalid rows rather than crashing the whole history page.
            continue

        summaries.append(
            AssessmentSummary(
                assessment_id=assessment.assessment_id,
                vendor_id=assessment.vendor_id,
                vendor_name=assessment.vendor_name,
                risk_tier=assessment.risk_tier,
                risk_score=(
                    assessment.risk_assessment.risk_score
                    if assessment.risk_assessment
                    else None
                ),
                status=assessment.status,
                recommendation=(
                    assessment.recommendation.decision
                    if assessment.recommendation
                    else None
                ),
                pipeline_mode=_pipeline_mode(
                    assessment,
                ),
                created_at=assessment.created_at,
                updated_at=assessment.updated_at,
                reviewed_at=(
                    assessment.human_decision.decision_timestamp
                    if assessment.human_decision
                    else None
                ),
            )
        )

    return summaries