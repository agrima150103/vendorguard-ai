from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    Assessment,
    AssessmentSummary,
    HumanReviewRequest,
    StartAssessmentRequest,
    VendorListItem,
)
from app.repositories.assessment_repository import (
    get_assessment,
    list_assessments,
)
from app.services.assessment_service import (
    AssessmentNotFoundError,
    InvalidAssessmentStateError,
    start_assessment,
    submit_human_review,
)
from app.services.vendor_loader import (
    VendorDataError,
    VendorNotFoundError,
    get_vendor_list,
)


router = APIRouter(prefix="/api/v1", tags=["VendorGuard"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "vendorguard-api",
    }


@router.get("/vendors", response_model=list[VendorListItem])
def vendors() -> list[VendorListItem]:
    return get_vendor_list()


@router.post(
    "/assessments",
    response_model=Assessment,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    request: StartAssessmentRequest,
) -> Assessment:
    try:
        return start_assessment(request.vendor_id)
    except VendorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except VendorDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get(
    "/assessments",
    response_model=list[AssessmentSummary],
)
def assessments() -> list[AssessmentSummary]:
    return list_assessments()


@router.get(
    "/assessments/{assessment_id}",
    response_model=Assessment,
)
def assessment_detail(assessment_id: str) -> Assessment:
    assessment = get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found.",
        )

    return assessment


@router.post(
    "/assessments/{assessment_id}/review",
    response_model=Assessment,
)
def review_assessment(
    assessment_id: str,
    request: HumanReviewRequest,
) -> Assessment:
    try:
        return submit_human_review(assessment_id, request)
    except AssessmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidAssessmentStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc