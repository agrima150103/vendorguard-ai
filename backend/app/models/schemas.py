from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class RiskTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AssessmentStatus(str, Enum):
    PENDING = "PENDING"
    EXTRACTING_EVIDENCE = "EXTRACTING_EVIDENCE"
    ANALYSING_RISK = "ANALYSING_RISK"
    CHECKING_POLICY = "CHECKING_POLICY"
    GENERATING_RECOMMENDATION = "GENERATING_RECOMMENDATION"
    AWAITING_HUMAN_REVIEW = "AWAITING_HUMAN_REVIEW"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class RecommendationDecision(str, Enum):
    APPROVE = "APPROVE"
    APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    REJECT = "REJECT"


class HumanDecisionValue(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    INFORMATION_REQUESTED = "INFORMATION_REQUESTED"
    REJECTED = "REJECTED"


class VendorContacts(StrictModel):
    primary: str | None = None
    security: str | None = None
    incident_response: str | None = None


class VendorProfile(StrictModel):
    vendor_id: str
    company_name: str
    registration_number: str | None = None
    founded: str | None = None
    headquarters: str | None = None
    employees: int | None = Field(default=None, ge=0)
    service_type: str
    data_access: str
    annual_revenue_usd: float | None = Field(default=None, ge=0)
    risk_tier: RiskTier
    documents_provided: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    contacts: VendorContacts | None = None


class EvidenceItem(StrictModel):
    evidence_id: str = Field(default_factory=lambda: f"EV-{uuid4().hex[:8].upper()}")
    claim: str
    source_name: str
    source_location: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["supported", "unsupported", "contradicted", "unverifiable"]
    contradicts: str | None = None


class EvidenceLedger(StrictModel):
    assessment_id: str
    vendor_id: str
    items: list[EvidenceItem] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    extraction_timestamp: datetime = Field(default_factory=utc_now)


class SecurityFinding(StrictModel):
    finding_id: str = Field(default_factory=lambda: f"SF-{uuid4().hex[:8].upper()}")
    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    finding_type: Literal[
        "prompt_injection", "missing_evidence", "contradiction",
        "unsupported_claim", "compliance_gap", "data_risk", "operational_risk"
    ]
    evidence_ids: list[str] = Field(default_factory=list)
    policy_rule_ids: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    matched_text: str | None = None


class RiskAssessment(StrictModel):
    assessment_id: str
    vendor_id: str
    findings: list[SecurityFinding] = Field(default_factory=list)
    risk_score: int = Field(ge=0, le=100)
    prompt_injection_detected: bool = False
    analysis_timestamp: datetime = Field(default_factory=utc_now)


class PolicyViolation(StrictModel):
    rule_id: str
    rule_name: str
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    mitigating_conditions: list[str] = Field(default_factory=list)


class PolicyCheckResult(StrictModel):
    assessment_id: str
    vendor_id: str
    violations: list[PolicyViolation] = Field(default_factory=list)
    passed_rules: list[str] = Field(default_factory=list)
    missing_mandatory_documents: list[str] = Field(default_factory=list)
    check_timestamp: datetime = Field(default_factory=utc_now)


class AssessmentRecommendation(StrictModel):
    decision: RecommendationDecision
    rationale: str
    finding_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    human_approval_required: Literal[True] = True


class HumanDecision(StrictModel):
    assessment_id: str
    reviewer_id: str
    decision: HumanDecisionValue
    reason: str = Field(min_length=3)
    conditions: list[str] = Field(default_factory=list)
    decision_timestamp: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def conditional_approval_needs_conditions(self):
        if self.decision == HumanDecisionValue.APPROVED_WITH_CONDITIONS and not self.conditions:
            raise ValueError("Conditional approval requires at least one condition.")
        return self


class AuditEntry(StrictModel):
    timestamp: datetime = Field(default_factory=utc_now)
    event: str
    detail: str = ""


class Assessment(StrictModel):
    assessment_id: str = Field(default_factory=lambda: f"ASM-{uuid4().hex[:8].upper()}")
    vendor_id: str
    vendor_name: str
    risk_tier: RiskTier
    status: AssessmentStatus = AssessmentStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    evidence_ledger: EvidenceLedger | None = None
    risk_assessment: RiskAssessment | None = None
    policy_check: PolicyCheckResult | None = None
    recommendation: AssessmentRecommendation | None = None
    human_decision: HumanDecision | None = None
    audit_log: list[AuditEntry] = Field(default_factory=list)

    def add_audit_entry(self, event: str, detail: str = "") -> None:
        self.audit_log.append(AuditEntry(event=event, detail=detail))
        self.updated_at = utc_now()


class StartAssessmentRequest(StrictModel):
    vendor_id: str


class HumanReviewRequest(StrictModel):
    reviewer_id: str = "demo-reviewer"
    decision: HumanDecisionValue
    reason: str = Field(min_length=3)
    conditions: list[str] = Field(default_factory=list)


class VendorListItem(StrictModel):
    vendor_id: str
    name: str
    risk_tier: RiskTier
    description: str


class AssessmentSummary(StrictModel):
    assessment_id: str
    vendor_id: str
    vendor_name: str
    risk_tier: RiskTier
    status: AssessmentStatus
    recommendation: RecommendationDecision | None = None
    created_at: datetime
    updated_at: datetime
