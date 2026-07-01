from __future__ import annotations

import re


INJECTION_PATTERNS: list[tuple[str, str]] = [
    (
        r"ignore\s+(?:all\s+)?previous",
        "override_instruction",
    ),
    (
        r"important\s+system\s+directive",
        "system_directive",
    ),
    (
        r"do\s+not\s+mention\s+this",
        "concealment",
    ),
    (
        r"mark\s+.+\s+as\s+approve",
        "forced_approval",
    ),
    (
        r"override\s+.+(?:decision|risk|reject|escalat)",
        "decision_override",
    ),
    (
        r"disregard\s+(?:all|any|previous)",
        "disregard_instruction",
    ),
    (
        (
            r"set\s+the\s+(?:final\s+)?decision"
            r"\s+to\s+approve"
        ),
        "forced_approval",
    ),
    (
        r"pre[-\s]?approved\s+by",
        "false_authority",
    ),
    (
        r"note\s+to\s+(?:ai|llm|system|model)",
        "direct_ai_address",
    ),
]


def scan_for_injection(
    document_name: str,
    content: str,
) -> str:
    """
    Detect prompt-injection patterns without following them.
    """

    findings: list[str] = []

    for line_number, line in enumerate(
        content.splitlines(),
        start=1,
    ):
        for pattern, injection_type in INJECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    "FINDING | "
                    f"line={line_number} | "
                    f"type={injection_type} | "
                    f"untrusted_text={line.strip()[:200]}"
                )
                break

    if not findings:
        return (
            f"INJECTION_CLEAR | source={document_name}"
        )

    return (
        f"INJECTION_DETECTED | source={document_name} | "
        "STATUS=BLOCKED_NOT_EXECUTED\n"
        + "\n".join(findings)
    )


def _retention_periods(
    content: str,
) -> list[tuple[float, str, str]]:
    records: list[tuple[float, str, str]] = []

    for line in content.splitlines():
        if not re.search(
            (
                r"retain|retention|delete|deletion|"
                r"deleted|expire"
            ),
            line,
            re.IGNORECASE,
        ):
            continue

        matches = re.findall(
            r"(\d+)\s*(day|month|year)s?",
            line,
            re.IGNORECASE,
        )

        for quantity, unit in matches:
            numeric_value = float(quantity)
            lower_unit = unit.lower()

            if lower_unit == "day":
                months = numeric_value / 30
            elif lower_unit == "year":
                months = numeric_value * 12
            else:
                months = numeric_value

            records.append(
                (
                    months,
                    f"{quantity} {unit}(s)",
                    line.strip()[:180],
                )
            )

    return records


def detect_contradictions(
    document_a_name: str,
    document_a_content: str,
    document_b_name: str,
    document_b_content: str,
) -> str:
    """
    Detect materially different retention periods across documents.
    """

    periods_a = _retention_periods(document_a_content)
    periods_b = _retention_periods(document_b_content)

    conflicts: list[str] = []

    for months_a, label_a, context_a in periods_a:
        for months_b, label_b, context_b in periods_b:
            if min(months_a, months_b) <= 0:
                continue

            ratio = (
                max(months_a, months_b)
                / min(months_a, months_b)
            )

            if (
                ratio >= 2
                and abs(months_a - months_b) >= 3
            ):
                conflicts.append(
                    "CONFLICT | "
                    f"{document_a_name}: {label_a} "
                    f"[{context_a}] | "
                    f"{document_b_name}: {label_b} "
                    f"[{context_b}]"
                )

    if not conflicts:
        return (
            "NO_CONTRADICTIONS | "
            f"between={document_a_name},{document_b_name}"
        )

    return (
        "CONTRADICTIONS_DETECTED | "
        f"between={document_a_name},{document_b_name} "
        f"| count={len(conflicts)}\n"
        + "\n".join(conflicts)
    )


def calculate_risk_score(
    base_tier: str,
    missing_document_count: int,
    prompt_injection_detected: bool,
    contradiction_detected: bool,
    no_incident_plan: bool,
    no_security_contact: bool,
) -> str:
    """
    Calculate a transparent risk score.
    """

    base_scores = {
        "LOW": 10,
        "MEDIUM": 30,
        "HIGH": 55,
    }

    tier = base_tier.upper()

    points: list[tuple[str, int]] = [
        (
            f"Base score ({tier})",
            base_scores.get(tier, 30),
        )
    ]

    if missing_document_count:
        points.append(
            (
                (
                    "Missing documents "
                    f"({missing_document_count} x 8)"
                ),
                missing_document_count * 8,
            )
        )

    if prompt_injection_detected:
        points.append(
            (
                "Prompt injection",
                30,
            )
        )

    if contradiction_detected:
        points.append(
            (
                "Retention contradiction",
                12,
            )
        )

    if no_incident_plan:
        points.append(
            (
                "No formal incident-response plan",
                10,
            )
        )

    if no_security_contact:
        points.append(
            (
                "No dedicated security contact",
                8,
            )
        )

    total = min(
        100,
        sum(value for _, value in points),
    )

    output = [
        f"RISK_SCORE | total={total}/100"
    ]

    output.extend(
        f"+{value} | {label}"
        for label, value in points
    )

    output.append(
        f"={total} | FINAL SCORE"
    )

    return "\n".join(output)


def mask_pii_for_logs(text: str) -> str:
    """Mask common sensitive values before logging."""

    masked = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text,
    )

    masked = re.sub(
        r"\b(?:\d[ -]?){13,16}\b",
        "[CARD]",
        masked,
    )

    masked = re.sub(
        r"\+?[\d\s().-]{10,17}",
        "[PHONE]",
        masked,
    )

    return masked