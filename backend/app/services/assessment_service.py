"""
VendorGuard AI — Assessment Service

This service coordinates the complete vendor-assessment workflow.

Workflow:
1. Load the vendor profile and documents.
2. Select the real ADK multi-agent pipeline when a Gemini key exists.
3. Safely fall back to deterministic tools if ADK cannot complete.
4. Store evidence, risk findings, policy results and recommendations.
5. Pause for mandatory human review.
6. Record the final human decision.

Important:
The agent produces a recommendation only.
A human reviewer always makes the final decision.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from app.models.schemas import (
    Assessment,
    AssessmentRecommendation,
    AssessmentStatus,
    EvidenceItem,
    EvidenceLedger,
    HumanDecision,
    HumanReviewRequest,
    PolicyCheckResult,
    PolicyViolation,
    RecommendationDecision,
    RiskAssessment,
    SecurityFinding,
)
from app.repositories.assessment_repository import (
    get_assessment,
    save_assessment,
)
from app.services.vendor_loader import (
    load_vendor_documents,
    load_vendor_profile,
)


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env",
    override=True,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class AssessmentNotFoundError(ValueError):
    """Raised when an assessment ID cannot be found."""


class InvalidAssessmentStateError(ValueError):
    """Raised when an assessment action is invalid for its current state."""


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _has_gemini_key() -> bool:
    """
    Return True when a non-placeholder Gemini API key is configured.

    The real API key must remain only inside the root .env file.
    """

    value = os.getenv(
        "GEMINI_API_KEY",
        "",
    ).strip()

    invalid_values = {
        "",
        "replace_with_your_key",
        "your_real_key_here",
        "your_actual_key_here",
        "PASTE_YOUR_FREE_AI_STUDIO_KEY_HERE",
    }

    return value not in invalid_values


def _friendly_adk_error(exc: Exception) -> str:
    """
    Convert internal ADK or Gemini exceptions into safe audit messages.
    """

    error_text = str(exc)
    error_text_upper = error_text.upper()

    if (
        "429" in error_text_upper
        or "RESOURCE_EXHAUSTED" in error_text_upper
        or "RATE LIMIT" in error_text_upper
        or "QUOTA" in error_text_upper
    ):
        return (
            "Gemini free-tier quota was temporarily unavailable. "
            "The assessment safely continued using the deterministic fallback."
        )

    if (
        "503" in error_text_upper
        or "UNAVAILABLE" in error_text_upper
        or "HIGH DEMAND" in error_text_upper
        or "SERVICE UNAVAILABLE" in error_text_upper
    ):
        return (
            "Gemini was temporarily unavailable because of high demand. "
            "The assessment safely continued using the deterministic fallback."
        )

    if (
        "API_KEY_INVALID" in error_text_upper
        or "INVALID API KEY" in error_text_upper
        or "API KEY NOT VALID" in error_text_upper
        or "UNAUTHENTICATED" in error_text_upper
        or "401" in error_text_upper
    ):
        return (
            "The Gemini API key could not be authenticated. "
            "The assessment safely continued using the deterministic fallback."
        )

    if (
        "MODEL_NOT_FOUND" in error_text_upper
        or "404" in error_text_upper
    ):
        return (
            "The configured Gemini model was unavailable. "
            "The assessment safely continued using the deterministic fallback."
        )

    if (
        "TIMEOUT" in error_text_upper
        or "DEADLINE_EXCEEDED" in error_text_upper
    ):
        return (
            "The ADK pipeline timed out before completion. "
            "The assessment safely continued using the deterministic fallback."
        )

    if (
        "MCP" in error_text_upper
        or "STDIO" in error_text_upper
    ):
        return (
            "The MCP policy connection could not complete. "
            "The assessment safely continued using the deterministic fallback."
        )

    return (
        "The ADK pipeline could not complete. "
        "The assessment safely continued using the deterministic fallback."
    )


# ---------------------------------------------------------------------------
# Deterministic fallback workflow
# ---------------------------------------------------------------------------

def _run_deterministic_assessment(
    assessment: Assessment,
    profile,
    documents: dict[str, str],
) -> Assessment:
    """
    Run the rule-based assessment pipeline.

    This remains available when:
    - no Gemini key is configured;
    - Gemini free-tier quota is unavailable;
    - the ADK pipeline fails;
    - the MCP policy connection fails.

    The fallback provides predictable demo behaviour and preserves the
    mandatory human-review gate.
    """

    from app.tools.evidence_tools import (
        check_missing_documents,
        extract_encryption_claims,
        extract_incident_response_claims,
        extract_retention_claims,
    )
    from app.tools.security_tools import (
        calculate_risk_score,
        detect_contradictions,
        scan_for_injection,
    )

    # -----------------------------------------------------------------------
    # Evidence extraction
    # -----------------------------------------------------------------------

    assessment.status = AssessmentStatus.EXTRACTING_EVIDENCE

    assessment.add_audit_entry(
        "EXTRACTING_EVIDENCE",
        "Deterministic evidence tools running.",
    )

    save_assessment(assessment)

    evidence_items: list[EvidenceItem] = []

    for document_name, content in documents.items():
        outputs = [
            extract_encryption_claims(
                document_name,
                content,
            ),
            extract_retention_claims(
                document_name,
                content,
            ),
            extract_incident_response_claims(
                document_name,
                content,
            ),
        ]

        for output in outputs:
            for line in output.splitlines():
                if not line.startswith("CLAIM |"):
                    continue

                fields: dict[str, str] = {}

                for piece in line.split("|")[1:]:
                    if "=" not in piece:
                        continue

                    key, value = piece.split(
                        "=",
                        1,
                    )

                    fields[key.strip()] = value.strip()

                evidence_items.append(
                    EvidenceItem(
                        evidence_id=fields.get("id"),
                        claim=fields.get(
                            "claim",
                            "Extracted evidence",
                        ),
                        source_name=fields.get(
                            "source",
                            document_name,
                        ),
                        source_location=fields.get(
                            "location",
                            "unknown",
                        ),
                        confidence=float(
                            fields.get(
                                "conf",
                                "0.75",
                            )
                        ),
                        status="supported",
                    )
                )

    document_check = check_missing_documents(
        profile.vendor_id,
        ", ".join(profile.documents_provided),
        profile.risk_tier.value,
        profile.service_type,
    )

    missing_documents: list[str] = []

    for line in document_check.splitlines():
        if not line.startswith("MISSING:"):
            continue

        value = line.split(
            ":",
            1,
        )[1].strip()

        if value.lower() != "none":
            missing_documents = [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

    assessment.evidence_ledger = EvidenceLedger(
        assessment_id=assessment.assessment_id,
        vendor_id=assessment.vendor_id,
        items=evidence_items,
        missing_evidence=missing_documents,
    )

    assessment.add_audit_entry(
        "EVIDENCE_EXTRACTED",
        f"{len(evidence_items)} evidence items extracted.",
    )

    save_assessment(assessment)

    # -----------------------------------------------------------------------
    # Risk and security analysis
    # -----------------------------------------------------------------------

    assessment.status = AssessmentStatus.ANALYSING_RISK

    assessment.add_audit_entry(
        "ANALYSING_RISK",
        "Deterministic security and risk tools running.",
    )

    save_assessment(assessment)

    findings: list[SecurityFinding] = []
    injection_detected = False

    for document_name, content in documents.items():
        injection_result = scan_for_injection(
            document_name,
            content,
        )

        if "INJECTION_DETECTED" in injection_result:
            injection_detected = True

            findings.append(
                SecurityFinding(
                    title=(
                        "Prompt-injection attempt "
                        "detected and blocked"
                    ),
                    description=(
                        "Untrusted instructions were found in "
                        f"{document_name} and were not executed."
                    ),
                    severity="critical",
                    finding_type="prompt_injection",
                    requires_human_review=True,
                    matched_text="[BLOCKED]",
                )
            )

    contradiction_detected = False
    document_names = list(documents.keys())

    for index, first_name in enumerate(document_names):
        remaining_names = document_names[index + 1:]

        for second_name in remaining_names:
            contradiction_result = detect_contradictions(
                first_name,
                documents[first_name],
                second_name,
                documents[second_name],
            )

            if (
                "CONTRADICTIONS_DETECTED"
                in contradiction_result
            ):
                contradiction_detected = True

                findings.append(
                    SecurityFinding(
                        title=(
                            "Conflicting retention "
                            "commitments"
                        ),
                        description=(
                            "Retention periods conflict between "
                            f"{first_name} and {second_name}."
                        ),
                        severity="high",
                        finding_type="contradiction",
                        requires_human_review=True,
                    )
                )

                break

        if contradiction_detected:
            break

    if missing_documents:
        findings.append(
            SecurityFinding(
                title="Mandatory evidence is missing",
                description=", ".join(missing_documents),
                severity="high",
                finding_type="missing_evidence",
                requires_human_review=True,
            )
        )

    no_incident_plan = (
        "incident response plan"
        in " ".join(missing_documents).lower()
    )

    incident_response_contact = getattr(
        profile.contacts,
        "incident_response",
        None,
    ) if profile.contacts else None

    no_security_contact = (
        not incident_response_contact
        or incident_response_contact.strip().upper()
        == "NOT PROVIDED"
    )

    score_text = calculate_risk_score(
        base_tier=profile.risk_tier.value,
        missing_document_count=len(
            missing_documents
        ),
        prompt_injection_detected=(
            injection_detected
        ),
        contradiction_detected=(
            contradiction_detected
        ),
        no_incident_plan=no_incident_plan,
        no_security_contact=(
            no_security_contact
        ),
    )

    score_match = re.search(
        r"=\s*(\d+)\s*\|\s*FINAL SCORE",
        score_text,
    )

    risk_score = (
        int(score_match.group(1))
        if score_match
        else 30
    )

    assessment.risk_assessment = RiskAssessment(
        assessment_id=assessment.assessment_id,
        vendor_id=assessment.vendor_id,
        findings=findings,
        risk_score=risk_score,
        prompt_injection_detected=(
            injection_detected
        ),
    )

    assessment.add_audit_entry(
        "RISK_ANALYSED",
        f"Risk score: {risk_score}.",
    )

    save_assessment(assessment)

    # -----------------------------------------------------------------------
    # Policy checking
    # -----------------------------------------------------------------------

    assessment.status = AssessmentStatus.CHECKING_POLICY

    assessment.add_audit_entry(
        "CHECKING_POLICY",
        "Deterministic policy checks running.",
    )

    save_assessment(assessment)

    violations: list[PolicyViolation] = []
    passed_rules: list[str] = [
        "HITL-001",
    ]

    if missing_documents:
        violations.append(
            PolicyViolation(
                rule_id="DOC-001",
                rule_name="Document completeness",
                severity="high",
                description=(
                    "Missing: "
                    + ", ".join(missing_documents)
                ),
            )
        )

    if contradiction_detected:
        violations.append(
            PolicyViolation(
                rule_id="RET-001",
                rule_name="Retention consistency",
                severity="medium",
                description=(
                    "Conflicting retention periods "
                    "must be reconciled."
                ),
            )
        )

    if profile.risk_tier.value == "MEDIUM":
        violations.append(
            PolicyViolation(
                rule_id="PAY-001",
                rule_name="PCI-DSS",
                severity="critical",
                description=(
                    "PCI-DSS certification or "
                    "SAQ was not provided."
                ),
            )
        )

    if profile.risk_tier.value == "HIGH":
        violations.append(
            PolicyViolation(
                rule_id="GDPR-001",
                rule_name="GDPR DPA",
                severity="critical",
                description=(
                    "A GDPR Data Processing "
                    "Agreement was not provided."
                ),
            )
        )

    assessment.policy_check = PolicyCheckResult(
        assessment_id=assessment.assessment_id,
        vendor_id=assessment.vendor_id,
        violations=violations,
        passed_rules=passed_rules,
        missing_mandatory_documents=(
            missing_documents
        ),
    )

    assessment.add_audit_entry(
        "POLICY_CHECKED",
        f"{len(violations)} violations found.",
    )

    save_assessment(assessment)

    # -----------------------------------------------------------------------
    # Recommendation
    # -----------------------------------------------------------------------

    assessment.status = (
        AssessmentStatus.GENERATING_RECOMMENDATION
    )

    assessment.add_audit_entry(
        "GENERATING_RECOMMENDATION",
        "Generating a non-binding recommendation.",
    )

    if (
        injection_detected
        or risk_score >= 71
    ):
        decision = (
            RecommendationDecision
            .ESCALATE_TO_HUMAN
        )

        rationale = (
            "Critical security findings or a high "
            "risk score require human escalation."
        )

    elif violations:
        decision = (
            RecommendationDecision
            .REQUEST_MORE_INFORMATION
        )

        rationale = (
            "Required evidence or policy gaps "
            "must be resolved before onboarding."
        )

    else:
        decision = (
            RecommendationDecision.APPROVE
        )

        rationale = (
            "No material deterministic policy gaps "
            "were identified. Human approval remains required."
        )

    assessment.recommendation = (
        AssessmentRecommendation(
            decision=decision,
            rationale=rationale,
            finding_ids=[
                item.finding_id
                for item in findings
            ],
            missing_evidence=(
                missing_documents
            ),
            confidence=(
                0.96
                if injection_detected
                else 0.90
                if violations
                else 0.84
            ),
            human_approval_required=True,
        )
    )

    assessment.add_audit_entry(
        "RECOMMENDATION_CREATED",
        decision.value,
    )

    save_assessment(assessment)

    return assessment


# ---------------------------------------------------------------------------
# ADK multi-agent workflow
# ---------------------------------------------------------------------------

def _run_adk_assessment(
    assessment: Assessment,
    profile,
    documents: dict[str, str],
) -> Assessment:
    """
    Run the real ADK multi-agent workflow.

    If the model, quota, MCP connection or agent runner fails, the workflow
    records a clear audit message and continues with deterministic tools.
    """

    from app.services.adk_runner import (
        run_assessment_sync,
    )

    assessment.status = (
        AssessmentStatus.EXTRACTING_EVIDENCE
    )

    assessment.add_audit_entry(
        "ADK_PIPELINE_STARTED",
        "Real ADK multi-agent pipeline started.",
    )

    save_assessment(assessment)

    try:
        result = run_assessment_sync(
            assessment_id=assessment.assessment_id,
            vendor_id=profile.vendor_id,
            vendor_name=profile.company_name,
            risk_tier=profile.risk_tier.value,
            service_type=profile.service_type,
            documents=documents,
            documents_provided=(
                profile.documents_provided
            ),
            missing_documents=(
                profile.missing_documents
            ),
        )

    except Exception as exc:
        logger.exception(
            "ADK pipeline failed; using deterministic fallback."
        )

        assessment.add_audit_entry(
            "ADK_PIPELINE_FAILED",
            _friendly_adk_error(exc),
        )

        save_assessment(assessment)

        return _run_deterministic_assessment(
            assessment,
            profile,
            documents,
        )

    assessment.evidence_ledger = (
        result["evidence_ledger"]
    )

    assessment.risk_assessment = (
        result["risk_assessment"]
    )

    assessment.policy_check = (
        result["policy_check"]
    )

    assessment.recommendation = (
        result["recommendation"]
    )

    agent_names = ", ".join(
        item["agent"]
        for item in result.get(
            "agent_timeline",
            [],
        )
    )

    assessment.add_audit_entry(
        "ADK_PIPELINE_COMPLETE",
        (
            agent_names
            or (
                "Evidence, risk, policy and "
                "recommendation agents completed."
            )
        ),
    )

    save_assessment(assessment)

    return assessment


# ---------------------------------------------------------------------------
# Public assessment operations
# ---------------------------------------------------------------------------

def start_assessment(
    vendor_id: str,
) -> Assessment:
    """
    Create and execute a new vendor assessment.

    ADK is selected when a valid Gemini key exists.
    Otherwise the deterministic fallback runs directly.
    """

    profile = load_vendor_profile(
        vendor_id
    )

    documents = load_vendor_documents(
        vendor_id
    )

    assessment = Assessment(
        vendor_id=profile.vendor_id,
        vendor_name=profile.company_name,
        risk_tier=profile.risk_tier,
    )

    assessment.add_audit_entry(
        "ASSESSMENT_CREATED",
        f"Created for {profile.company_name}.",
    )

    save_assessment(assessment)

    use_adk = _has_gemini_key()

    assessment.add_audit_entry(
        "PIPELINE_SELECTED",
        (
            "ADK multi-agent"
            if use_adk
            else "Deterministic fallback"
        ),
    )

    save_assessment(assessment)

    if use_adk:
        assessment = _run_adk_assessment(
            assessment,
            profile,
            documents,
        )
    else:
        assessment = (
            _run_deterministic_assessment(
                assessment,
                profile,
                documents,
            )
        )

    assessment.status = (
        AssessmentStatus
        .AWAITING_HUMAN_REVIEW
    )

    assessment.add_audit_entry(
        "AWAITING_HUMAN_REVIEW",
        (
            "Recommendation: "
            f"{assessment.recommendation.decision.value}. "
            "A human decision is required."
        ),
    )

    save_assessment(assessment)

    return assessment


def submit_human_review(
    assessment_id: str,
    request: HumanReviewRequest,
) -> Assessment:
    """
    Record the final human review.

    Only assessments currently waiting for human review may be completed.
    """

    assessment = get_assessment(
        assessment_id
    )

    if assessment is None:
        raise AssessmentNotFoundError(
            (
                f"Assessment {assessment_id} "
                "does not exist."
            )
        )

    if (
        assessment.status
        != AssessmentStatus
        .AWAITING_HUMAN_REVIEW
    ):
        raise InvalidAssessmentStateError(
            (
                "Assessment is not awaiting "
                "human review."
            )
        )

    assessment.human_decision = HumanDecision(
        assessment_id=assessment_id,
        reviewer_id=request.reviewer_id,
        decision=request.decision,
        reason=request.reason,
        conditions=request.conditions,
    )

    assessment.status = (
        AssessmentStatus.COMPLETE
    )

    assessment.add_audit_entry(
        "HUMAN_DECISION_RECORDED",
        (
            f"Reviewer {request.reviewer_id} "
            f"recorded {request.decision.value}."
        ),
    )

    save_assessment(assessment)

    return assessment
