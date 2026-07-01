from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


POLICIES_PATH = Path(__file__).with_name(
    "policies.json"
)

mcp = FastMCP(
    "vendorguard-policy-server"
)


def _load() -> dict:
    return json.loads(
        POLICIES_PATH.read_text(
            encoding="utf-8"
        )
    )


@mcp.tool()
def get_policy_rules(
    risk_tier: str,
) -> dict:
    """
    Return policy rules applicable to the supplied risk tier.
    """

    tier = risk_tier.upper()
    rules: list[dict] = []

    for rule in _load()["rules"]:
        applies_to = [
            item.lower()
            for item in rule.get(
                "applies_to",
                [],
            )
        ]

        applies = (
            "all" in applies_to
            or tier.lower() in applies_to
            or (
                tier == "HIGH"
                and "high_data_access" in applies_to
            )
            or (
                tier == "MEDIUM"
                and "payment" in applies_to
            )
        )

        if applies:
            rules.append(rule)

    return {
        "risk_tier": tier,
        "rules": rules,
        "total_count": len(rules),
    }


@mcp.tool()
def get_required_documents(
    risk_tier: str,
    service_type: str = "",
) -> dict:
    """
    Return mandatory documents for the vendor.
    """

    data = _load()["mandatory_documents"]

    tier = risk_tier.upper()
    service = service_type.lower()

    required = list(
        data["all_vendors"]
    )

    if (
        tier in {"MEDIUM", "HIGH"}
        or "payment" in service
    ):
        required.extend(
            data["payment_vendors"]
        )

    if (
        tier == "HIGH"
        or any(
            word in service
            for word in (
                "data",
                "analytics",
                "pii",
            )
        )
    ):
        required.extend(
            data["pii_vendors"]
        )

    if tier == "HIGH":
        required.extend(
            data["high_risk_vendors"]
        )

    return {
        "required_documents": list(
            dict.fromkeys(required)
        )
    }


@mcp.tool()
def get_policy_rule(
    rule_id: str,
) -> dict:
    """Return one policy rule."""

    for rule in _load()["rules"]:
        if (
            rule["rule_id"].upper()
            == rule_id.upper()
        ):
            return rule

    return {
        "error": "rule_not_found",
        "rule_id": rule_id,
    }


@mcp.tool()
def get_risk_thresholds() -> dict:
    """
    Return score-to-recommendation thresholds.
    """

    return _load()["risk_thresholds"]


@mcp.tool()
def check_policy_compliance(
    vendor_id: str,
    risk_tier: str,
    provided_documents: str,
    claimed_encryption: bool,
    has_incident_response_contact: bool,
    has_incident_response_plan: bool,
    has_retention_consistency: bool,
) -> dict:
    """
    Perform a deterministic policy compliance check.
    """

    tier = risk_tier.upper()
    supplied = provided_documents.lower()

    violations: list[dict] = []
    passed_rules: list[str] = []

    checks = [
        (
            "SEC-001",
            claimed_encryption,
            "Encryption at rest",
            (
                "No specific encryption evidence "
                "was found."
            ),
            "high",
        ),
        (
            "IR-001",
            has_incident_response_contact,
            "Incident response contact",
            (
                "No dedicated incident-response "
                "contact was provided."
            ),
            "high",
        ),
        (
            "IR-002",
            has_incident_response_plan,
            "Incident response plan",
            (
                "No formal written incident-response "
                "plan was found."
            ),
            "high",
        ),
        (
            "RET-001",
            has_retention_consistency,
            "Retention consistency",
            (
                "Conflicting retention periods "
                "were detected."
            ),
            "medium",
        ),
    ]

    for (
        rule_id,
        passed,
        name,
        description,
        severity,
    ) in checks:
        if passed:
            passed_rules.append(rule_id)
        else:
            violations.append(
                {
                    "rule_id": rule_id,
                    "rule_name": name,
                    "severity": severity,
                    "description": description,
                }
            )

    if tier == "MEDIUM":
        has_pci = any(
            word in supplied
            for word in (
                "pci",
                "saq",
            )
        )

        if has_pci:
            passed_rules.append("PAY-001")
        else:
            violations.append(
                {
                    "rule_id": "PAY-001",
                    "rule_name": (
                        "PCI-DSS for payment vendors"
                    ),
                    "severity": "critical",
                    "description": (
                        "PCI-DSS certification or "
                        "SAQ was not provided."
                    ),
                }
            )

    if tier == "HIGH":
        has_dpa = any(
            word in supplied
            for word in (
                "dpa",
                "data processing agreement",
                "gdpr",
            )
        )

        if has_dpa:
            passed_rules.append("GDPR-001")
        else:
            violations.append(
                {
                    "rule_id": "GDPR-001",
                    "rule_name": (
                        "GDPR Data Processing Agreement"
                    ),
                    "severity": "critical",
                    "description": (
                        "A GDPR DPA was not provided."
                    ),
                }
            )

    passed_rules.append("HITL-001")

    critical_count = sum(
        item["severity"] == "critical"
        for item in violations
    )

    high_count = sum(
        item["severity"] == "high"
        for item in violations
    )

    if critical_count > 0 or high_count >= 2:
        verdict = "ESCALATE_TO_HUMAN"
    elif violations:
        verdict = "REQUEST_MORE_INFORMATION"
    elif tier == "LOW":
        verdict = "APPROVE"
    else:
        verdict = "APPROVE_WITH_CONDITIONS"

    return {
        "vendor_id": vendor_id,
        "risk_tier": tier,
        "policy_verdict": verdict,
        "violations": violations,
        "passed_rules": passed_rules,
        "total_violations": len(violations),
    }


@mcp.resource("policy://vendor-onboarding")
def vendor_policy() -> str:
    """
    Expose the complete policy document.
    """

    return POLICIES_PATH.read_text(
        encoding="utf-8"
    )


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )