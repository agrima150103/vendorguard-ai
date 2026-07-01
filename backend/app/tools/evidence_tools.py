from __future__ import annotations

import re
from uuid import uuid4


def _line_records(
    document_name: str,
    content: str,
    patterns: list[tuple[str, str]],
) -> list[dict]:
    records: list[dict] = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        for pattern, label in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                records.append(
                    {
                        "evidence_id": (
                            f"EV-{uuid4().hex[:8].upper()}"
                        ),
                        "claim": label,
                        "source_name": document_name,
                        "source_location": f"line {line_number}",
                        "raw_text": line.strip()[:240],
                        "confidence": 0.82,
                    }
                )
                break

    return records


def _format(
    evidence_type: str,
    document_name: str,
    records: list[dict],
) -> str:
    if not records:
        return (
            f"NO_{evidence_type}_EVIDENCE "
            f"| source={document_name}"
        )

    output = [
        (
            f"{evidence_type}_EVIDENCE "
            f"| source={document_name} "
            f"| count={len(records)}"
        )
    ]

    for item in records:
        output.append(
            "CLAIM | "
            f"id={item['evidence_id']} | "
            f"claim={item['claim']} | "
            f"source={item['source_name']} | "
            f"location={item['source_location']} | "
            f"conf={item['confidence']} | "
            f"text={item['raw_text']}"
        )

    return "\n".join(output)


def extract_encryption_claims(
    document_name: str,
    content: str,
) -> str:
    """
    Extract encryption-related evidence with document and line references.
    """

    records = _line_records(
        document_name,
        content,
        [
            (
                r"\bAES[-\s]?256\b",
                "AES-256 encryption is claimed",
            ),
            (
                (
                    r"encrypt(?:ed|ion).{0,30}\bat rest\b"
                    r"|\bat rest.{0,30}encrypt"
                ),
                "Encryption at rest is claimed",
            ),
            (
                (
                    r"encrypt(?:ed|ion).{0,30}\bin transit\b"
                    r"|\bin transit.{0,30}encrypt"
                ),
                "Encryption in transit is claimed",
            ),
            (
                r"\bTLS\s*1\.[23]\b",
                "TLS 1.2 or higher is claimed",
            ),
            (
                r"\bKMS\b|key management|key rotation",
                "Key-management controls are claimed",
            ),
        ],
    )

    return _format(
        "ENCRYPTION",
        document_name,
        records,
    )


def extract_retention_claims(
    document_name: str,
    content: str,
) -> str:
    """
    Extract retention and deletion periods with source references.
    """

    records = _line_records(
        document_name,
        content,
        [
            (
                (
                    r"(?:retain|retention|kept).{0,100}"
                    r"\b\d+\s*(?:day|month|year)s?\b"
                ),
                "A retention period is stated",
            ),
            (
                (
                    r"(?:delete|deletion|deleted|expire).{0,100}"
                    r"\b\d+\s*(?:day|month|year)s?\b"
                ),
                "A deletion period is stated",
            ),
        ],
    )

    return _format(
        "RETENTION",
        document_name,
        records,
    )


def extract_incident_response_claims(
    document_name: str,
    content: str,
) -> str:
    """
    Extract incident-response plans, contacts and notification commitments.
    """

    records = _line_records(
        document_name,
        content,
        [
            (
                r"incident response (?:plan|procedure|team|contact)",
                "Incident-response capability is described",
            ),
            (
                r"notify.{0,50}\b\d+\s*(?:hour|day)s?\b",
                "A breach-notification timeline is stated",
            ),
            (
                (
                    r"\b(?:security|incident)[\w.-]*"
                    r"@[\w.-]+\.[A-Za-z]{2,}\b"
                ),
                "A dedicated security contact is supplied",
            ),
            (
                r"\bDPO\b|data protection officer",
                "A data-protection role is identified",
            ),
        ],
    )

    return _format(
        "INCIDENT_RESPONSE",
        document_name,
        records,
    )


def check_missing_documents(
    vendor_id: str,
    documents_provided: str,
    risk_tier: str,
    service_type: str = "",
) -> str:
    """
    Compare supplied filenames with risk-appropriate requirements.
    """

    supplied = documents_provided.lower()
    tier = risk_tier.upper()
    service = service_type.lower()

    requirements: list[tuple[str, list[str]]] = [
        (
            "Security questionnaire",
            [
                "security_questionnaire",
                "security questionnaire",
            ],
        ),
        (
            "Privacy policy",
            [
                "privacy_policy",
                "privacy policy",
            ],
        ),
    ]

    if tier in {"MEDIUM", "HIGH"} or "payment" in service:
        requirements.extend(
            [
                (
                    "PCI-DSS certificate or SAQ",
                    ["pci", "saq"],
                ),
                (
                    "Incident response plan",
                    [
                        "incident_response",
                        "incident response",
                    ],
                ),
            ]
        )

    if tier == "HIGH" or any(
        word in service
        for word in ("data", "analytics", "pii")
    ):
        requirements.extend(
            [
                (
                    "GDPR Data Processing Agreement",
                    [
                        "dpa",
                        "data_processing_agreement",
                    ],
                ),
                (
                    "Subprocessor list",
                    ["subprocessor"],
                ),
            ]
        )

    if tier == "HIGH":
        requirements.extend(
            [
                (
                    "Penetration test report",
                    [
                        "penetration",
                        "pentest",
                    ],
                ),
                (
                    "ISO 27001 or SOC 2 report",
                    [
                        "iso",
                        "soc2",
                        "soc_2",
                    ],
                ),
            ]
        )

    present: list[str] = []
    missing: list[str] = []

    for label, aliases in requirements:
        found = any(alias in supplied for alias in aliases)

        if found:
            present.append(label)
        else:
            missing.append(label)

    return (
        f"DOCUMENT_CHECK | vendor={vendor_id} | tier={tier}\n"
        f"PRESENT: {', '.join(present) or 'none'}\n"
        f"MISSING: {', '.join(missing) or 'none'}"
    )