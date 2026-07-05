import { useEffect, useState } from "react";

import {
  getAssessment,
  getVendors,
  startAssessment,
  submitReview,
} from "./api";

import AssessmentHistory from "./AssessmentHistory";
import HomePage from "./HomePage";
import "./styles.css";


const RISK_META = {
  LOW: {
    label: "LOW RISK",
    color: "#4ade80",
    background: "#0d2b1f",
    border: "#16a34a",
  },
  MEDIUM: {
    label: "MEDIUM RISK",
    color: "#fbbf24",
    background: "#2b1f00",
    border: "#d97706",
  },
  HIGH: {
    label: "HIGH RISK",
    color: "#f87171",
    background: "#2b0d0d",
    border: "#dc2626",
  },
};


const RECOMMENDATION_META = {
  APPROVE: {
    label: "Approve",
    color: "#4ade80",
    background: "#0d2b1f",
    border: "#16a34a",
  },
  APPROVE_WITH_CONDITIONS: {
    label: "Approve with conditions",
    color: "#a78bfa",
    background: "#1a0d2b",
    border: "#7c3aed",
  },
  REQUEST_MORE_INFORMATION: {
    label: "Request more information",
    color: "#fbbf24",
    background: "#2b1f00",
    border: "#d97706",
  },
  ESCALATE_TO_HUMAN: {
    label: "Escalate to human",
    color: "#f87171",
    background: "#2b0d0d",
    border: "#dc2626",
  },
  REJECT: {
    label: "Reject",
    color: "#fb7185",
    background: "#2b0d14",
    border: "#e11d48",
  },
};


const HUMAN_DECISION_META = {
  APPROVED: {
    label: "Approved",
    color: "#4ade80",
    background: "#0d2b1f",
    border: "#16a34a",
  },
  APPROVED_WITH_CONDITIONS: {
    label: "Approved with conditions",
    color: "#a78bfa",
    background: "#1a0d2b",
    border: "#7c3aed",
  },
  INFORMATION_REQUESTED: {
    label: "Information requested",
    color: "#fbbf24",
    background: "#2b1f00",
    border: "#d97706",
  },
  REJECTED: {
    label: "Rejected",
    color: "#f87171",
    background: "#2b0d0d",
    border: "#dc2626",
  },
};


const SEVERITY_COLORS = {
  critical: "#fb7185",
  high: "#f87171",
  medium: "#fbbf24",
  low: "#4ade80",
};


function formatLabel(value) {
  if (!value) {
    return "—";
  }

  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


function getPipelineState(auditLog = []) {
  const events = auditLog.map((entry) => entry.event);
  const selectedEntry = auditLog.find(
    (entry) => entry.event === "PIPELINE_SELECTED",
  );

  if (events.includes("ADK_PIPELINE_COMPLETE")) {
    return {
      type: "adk_complete",
      label: "ADK completed",
      color: "#4ade80",
      background: "#0d2b1f",
      border: "#16a34a",
      description:
        "The Gemini-powered ADK multi-agent workflow completed successfully.",
    };
  }

  if (events.includes("ADK_PIPELINE_FAILED")) {
    const failedEntry = auditLog.find(
      (entry) => entry.event === "ADK_PIPELINE_FAILED",
    );

    return {
      type: "fallback",
      label: "Fallback used",
      color: "#fbbf24",
      background: "#2b1f00",
      border: "#d97706",
      description:
        failedEntry?.detail ||
        "The ADK pipeline could not complete, so deterministic safety controls completed the assessment.",
    };
  }

  if (
    selectedEntry?.detail
      ?.toLowerCase()
      .includes("deterministic")
  ) {
    return {
      type: "deterministic",
      label: "Deterministic mode",
      color: "#94a3b8",
      background: "#111827",
      border: "#475569",
      description:
        "The assessment was completed using local deterministic evidence, security and policy rules.",
    };
  }

  if (events.includes("ADK_PIPELINE_STARTED")) {
    return {
      type: "adk_running",
      label: "ADK running",
      color: "#60a5fa",
      background: "#0c1c35",
      border: "#2563eb",
      description:
        "The Gemini-powered multi-agent workflow is currently running.",
    };
  }

  return {
    type: "unknown",
    label: "Pipeline pending",
    color: "#94a3b8",
    background: "#111827",
    border: "#475569",
    description:
      "The assessment pipeline has not reported its final execution mode yet.",
  };
}


function RiskBadge({ tier }) {
  const meta = RISK_META[tier] || RISK_META.LOW;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        width: "fit-content",
        padding: "4px 10px",
        borderRadius: 999,
        border: `1px solid ${meta.border}`,
        background: meta.background,
        color: meta.color,
        fontSize: 11,
        fontWeight: 800,
        letterSpacing: "0.06em",
      }}
    >
      {meta.label}
    </span>
  );
}


function PipelineBadge({ auditLog }) {
  const pipeline = getPipelineState(auditLog);

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        width: "fit-content",
        padding: "6px 11px",
        borderRadius: 999,
        border: `1px solid ${pipeline.border}`,
        background: pipeline.background,
        color: pipeline.color,
        fontSize: 12,
        fontWeight: 800,
      }}
    >
      <span
        style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: pipeline.color,
        }}
      />

      {pipeline.label}
    </span>
  );
}


function PipelineNotice({ auditLog }) {
  const pipeline = getPipelineState(auditLog);

  return (
    <div
      style={{
        marginBottom: 20,
        padding: "14px 16px",
        borderRadius: 10,
        border: `1px solid ${pipeline.border}`,
        background: pipeline.background,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 6,
        }}
      >
        <PipelineBadge auditLog={auditLog} />

        <strong
          style={{
            color: pipeline.color,
            fontSize: 13,
          }}
        >
          Assessment execution mode
        </strong>
      </div>

      <p
        style={{
          margin: 0,
          color: "#cbd5e1",
          fontSize: 13,
          lineHeight: 1.6,
        }}
      >
        {pipeline.description}
      </p>

      {pipeline.type === "fallback" && (
        <p
          style={{
            margin: "8px 0 0",
            color: "#94a3b8",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          No assessment data was lost. Evidence extraction, risk
          scoring, policy checks and mandatory human review continued
          through the deterministic safety pipeline.
        </p>
      )}
    </div>
  );
}


function ScoreCircle({ score = 0 }) {
  const normalizedScore = Math.min(
    Math.max(Number(score) || 0, 0),
    100,
  );

  const color =
    normalizedScore >= 70
      ? "#f87171"
      : normalizedScore >= 40
        ? "#fbbf24"
        : "#4ade80";

  return (
    <div
      style={{
        width: 112,
        height: 112,
        borderRadius: "50%",
        border: `9px solid ${color}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        boxShadow: `0 0 28px ${color}22`,
      }}
    >
      <strong
        style={{
          color,
          fontSize: 28,
          lineHeight: 1,
        }}
      >
        {normalizedScore}
      </strong>

      <span
        style={{
          color: "#64748b",
          fontSize: 11,
          marginTop: 4,
        }}
      >
        /100
      </span>
    </div>
  );
}


function SummaryCard({ title, children }) {
  return (
    <div
      style={{
        background: "#0f1d30",
        border: "1px solid #21334c",
        borderRadius: 14,
        padding: 20,
      }}
    >
      <p
        style={{
          margin: "0 0 10px",
          color: "#64748b",
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
      >
        {title}
      </p>

      {children}
    </div>
  );
}


function StatRow({ label, value, color = "#e2e8f0" }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: 14,
        padding: "7px 0",
        borderBottom: "1px solid #1e293b",
      }}
    >
      <span
        style={{
          color: "#64748b",
          fontSize: 12,
        }}
      >
        {label}
      </span>

      <strong
        style={{
          color,
          fontSize: 12,
          textAlign: "right",
        }}
      >
        {value}
      </strong>
    </div>
  );
}


function EvidencePanel({ ledger }) {
  const items = ledger?.items || [];
  const missing = ledger?.missing_evidence || [];

  return (
    <div>
      <h3 style={sectionHeadingStyle}>
        Evidence ledger
      </h3>

      {items.length === 0 && (
        <EmptyState text="No structured evidence items were extracted." />
      )}

      {items.map((item, index) => {
        const contradicted = item.status === "contradicted";
        const supported = item.status === "supported";

        const statusColor = contradicted
          ? "#f87171"
          : supported
            ? "#4ade80"
            : "#94a3b8";

        return (
          <div
            key={item.evidence_id || index}
            style={{
              background: "#091320",
              border: `1px solid ${
                contradicted
                  ? "#7f1d1d"
                  : supported
                    ? "#14532d"
                    : "#26364d"
              }`,
              borderRadius: 10,
              padding: 14,
              marginBottom: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 10,
              }}
            >
              <span
                style={{
                  padding: "3px 8px",
                  borderRadius: 999,
                  border: `1px solid ${statusColor}`,
                  color: statusColor,
                  fontSize: 10,
                  fontWeight: 800,
                  textTransform: "uppercase",
                  flexShrink: 0,
                }}
              >
                {item.status || "unknown"}
              </span>

              <p
                style={{
                  margin: 0,
                  color: "#e2e8f0",
                  fontSize: 13,
                  lineHeight: 1.55,
                }}
              >
                {item.claim}
              </p>
            </div>

            <div
              style={{
                marginTop: 10,
                display: "flex",
                flexWrap: "wrap",
                gap: 16,
              }}
            >
              <span
                style={{
                  color: "#60a5fa",
                  fontSize: 11,
                }}
              >
                Source: {item.source_name || "Unknown"}
                {item.source_location
                  ? ` · ${item.source_location}`
                  : ""}
              </span>

              {item.confidence !== undefined && (
                <span
                  style={{
                    color: "#64748b",
                    fontSize: 11,
                  }}
                >
                  Confidence:{" "}
                  {Math.round(
                    Number(item.confidence) * 100,
                  )}
                  %
                </span>
              )}
            </div>
          </div>
        );
      })}

      {missing.length > 0 && (
        <div
          style={{
            marginTop: 16,
            background: "#241800",
            border: "1px solid #854d0e",
            borderRadius: 10,
            padding: 14,
          }}
        >
          <strong
            style={{
              color: "#fbbf24",
              fontSize: 13,
            }}
          >
            Missing evidence
          </strong>

          {missing.map((item, index) => (
            <p
              key={`${item}-${index}`}
              style={{
                margin: "7px 0 0",
                color: "#d6a84b",
                fontSize: 12,
              }}
            >
              • {item}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}


function SecurityPanel({ riskAssessment }) {
  const findings = riskAssessment?.findings || [];
  const injectionDetected =
    riskAssessment?.prompt_injection_detected;

  return (
    <div>
      <h3 style={sectionHeadingStyle}>
        Security and risk findings
      </h3>

      {injectionDetected && (
        <div
          style={{
            marginBottom: 14,
            padding: 16,
            background: "#2b0d0d",
            border: "1px solid #dc2626",
            borderRadius: 10,
          }}
        >
          <strong
            style={{
              color: "#f87171",
              fontSize: 14,
            }}
          >
            Prompt-injection attempt blocked
          </strong>

          <p
            style={{
              margin: "7px 0 0",
              color: "#cbd5e1",
              fontSize: 12,
              lineHeight: 1.6,
            }}
          >
            A vendor-controlled document contained instructions
            attempting to influence the assessment. The text was
            treated as untrusted evidence and was not executed.
          </p>
        </div>
      )}

      {findings.length === 0 && !injectionDetected && (
        <EmptyState text="No material security findings were detected." />
      )}

      {findings.map((finding, index) => {
        const severity =
          String(finding.severity || "medium").toLowerCase();

        const color =
          SEVERITY_COLORS[severity] || "#94a3b8";

        return (
          <div
            key={finding.finding_id || index}
            style={{
              marginBottom: 10,
              padding: 14,
              background: "#091320",
              border: "1px solid #26364d",
              borderLeft: `4px solid ${color}`,
              borderRadius: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 9,
                flexWrap: "wrap",
              }}
            >
              <strong
                style={{
                  color: "#e2e8f0",
                  fontSize: 13,
                }}
              >
                {finding.title}
              </strong>

              <span
                style={{
                  color,
                  fontSize: 10,
                  fontWeight: 800,
                  textTransform: "uppercase",
                }}
              >
                {severity}
              </span>
            </div>

            <p
              style={{
                margin: "7px 0 0",
                color: "#94a3b8",
                fontSize: 12,
                lineHeight: 1.6,
              }}
            >
              {finding.description}
            </p>
          </div>
        );
      })}
    </div>
  );
}


function PolicyPanel({ policyCheck }) {
  const violations = policyCheck?.violations || [];
  const passedRules = policyCheck?.passed_rules || [];
  const missingDocuments =
    policyCheck?.missing_mandatory_documents || [];

  return (
    <div>
      <h3 style={sectionHeadingStyle}>
        Policy results
      </h3>

      {violations.length === 0 && (
        <div
          style={{
            padding: 14,
            marginBottom: 14,
            background: "#0d2b1f",
            border: "1px solid #16a34a",
            borderRadius: 10,
            color: "#4ade80",
            fontSize: 13,
          }}
        >
          No policy violations were identified.
        </div>
      )}

      {violations.map((violation, index) => {
        const severity =
          String(violation.severity || "medium").toLowerCase();

        const color =
          SEVERITY_COLORS[severity] || "#94a3b8";

        return (
          <div
            key={`${violation.rule_id}-${index}`}
            style={{
              marginBottom: 10,
              padding: 14,
              background: "#091320",
              border: "1px solid #26364d",
              borderLeft: `4px solid ${color}`,
              borderRadius: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <strong
                style={{
                  color: "#e2e8f0",
                  fontSize: 13,
                }}
              >
                {violation.rule_id}
              </strong>

              <span
                style={{
                  color,
                  fontSize: 10,
                  fontWeight: 800,
                  textTransform: "uppercase",
                }}
              >
                {severity}
              </span>

              <span
                style={{
                  color: "#94a3b8",
                  fontSize: 12,
                }}
              >
                {violation.rule_name}
              </span>
            </div>

            <p
              style={{
                margin: "7px 0 0",
                color: "#94a3b8",
                fontSize: 12,
                lineHeight: 1.6,
              }}
            >
              {violation.description}
            </p>
          </div>
        );
      })}

      {passedRules.length > 0 && (
        <>
          <h4
            style={{
              margin: "20px 0 10px",
              color: "#64748b",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: "0.07em",
            }}
          >
            Passed rules
          </h4>

          <div
            style={{
              display: "flex",
              gap: 7,
              flexWrap: "wrap",
            }}
          >
            {passedRules.map((rule, index) => (
              <span
                key={`${rule}-${index}`}
                style={{
                  padding: "5px 9px",
                  background: "#0d2b1f",
                  border: "1px solid #16a34a",
                  borderRadius: 999,
                  color: "#4ade80",
                  fontSize: 11,
                  fontWeight: 700,
                }}
              >
                ✓ {rule}
              </span>
            ))}
          </div>
        </>
      )}

      {missingDocuments.length > 0 && (
        <div
          style={{
            marginTop: 18,
            padding: 14,
            background: "#241800",
            border: "1px solid #854d0e",
            borderRadius: 10,
          }}
        >
          <strong
            style={{
              color: "#fbbf24",
              fontSize: 13,
            }}
          >
            Missing mandatory documents
          </strong>

          {missingDocuments.map((item, index) => (
            <p
              key={`${item}-${index}`}
              style={{
                color: "#d6a84b",
                fontSize: 12,
                margin: "7px 0 0",
              }}
            >
              • {item}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}


function AuditTimeline({ auditLog = [] }) {
  const eventMeta = {
    ASSESSMENT_CREATED: {
      label: "Assessment created",
      color: "#94a3b8",
    },
    PIPELINE_SELECTED: {
      label: "Pipeline selected",
      color: "#60a5fa",
    },
    ADK_PIPELINE_STARTED: {
      label: "ADK pipeline started",
      color: "#60a5fa",
    },
    ADK_PIPELINE_COMPLETE: {
      label: "ADK pipeline complete",
      color: "#4ade80",
    },
    ADK_PIPELINE_FAILED: {
      label: "ADK unavailable — fallback activated",
      color: "#fbbf24",
    },
    EXTRACTING_EVIDENCE: {
      label: "Evidence extraction",
      color: "#a78bfa",
    },
    EVIDENCE_EXTRACTED: {
      label: "Evidence extracted",
      color: "#a78bfa",
    },
    ANALYSING_RISK: {
      label: "Risk and security analysis",
      color: "#fbbf24",
    },
    RISK_ANALYSED: {
      label: "Risk analysis complete",
      color: "#fbbf24",
    },
    CHECKING_POLICY: {
      label: "Policy checks",
      color: "#34d399",
    },
    POLICY_CHECKED: {
      label: "Policy checks complete",
      color: "#34d399",
    },
    GENERATING_RECOMMENDATION: {
      label: "Generating recommendation",
      color: "#60a5fa",
    },
    RECOMMENDATION_CREATED: {
      label: "Recommendation created",
      color: "#60a5fa",
    },
    AWAITING_HUMAN_REVIEW: {
      label: "Awaiting human review",
      color: "#fbbf24",
    },
    HUMAN_DECISION_RECORDED: {
      label: "Human decision recorded",
      color: "#4ade80",
    },
  };

  return (
    <div>
      <h3 style={sectionHeadingStyle}>
        Audit trail
      </h3>

      {auditLog.map((entry, index) => {
        const meta =
          eventMeta[entry.event] || {
            label: formatLabel(entry.event),
            color: "#94a3b8",
          };

        return (
          <div
            key={`${entry.event}-${index}`}
            style={{
              display: "grid",
              gridTemplateColumns: "28px 1fr",
              gap: 12,
              position: "relative",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                flexDirection: "column",
              }}
            >
              <div
                style={{
                  width: 11,
                  height: 11,
                  borderRadius: "50%",
                  background: meta.color,
                  marginTop: 5,
                  flexShrink: 0,
                }}
              />

              {index < auditLog.length - 1 && (
                <div
                  style={{
                    width: 2,
                    minHeight: 52,
                    flex: 1,
                    background: "#26364d",
                    marginTop: 5,
                  }}
                />
              )}
            </div>

            <div
              style={{
                paddingBottom: 20,
              }}
            >
              <strong
                style={{
                  color: meta.color,
                  fontSize: 13,
                }}
              >
                {meta.label}
              </strong>

              <p
                style={{
                  margin: "5px 0 0",
                  color: "#94a3b8",
                  fontSize: 12,
                  lineHeight: 1.55,
                }}
              >
                {entry.detail}
              </p>

              {entry.timestamp && (
                <span
                  style={{
                    display: "block",
                    color: "#475569",
                    fontSize: 10,
                    marginTop: 5,
                  }}
                >
                  {new Date(
                    entry.timestamp,
                  ).toLocaleString()}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}


function HumanReviewPanel({
  assessment,
  submitting,
  onSubmit,
}) {
  const [reviewerName, setReviewerName] = useState("");
  const [reviewerRole, setReviewerRole] = useState("");
  const [decision, setDecision] = useState(
    "INFORMATION_REQUESTED",
  );
  const [reason, setReason] = useState("");
  const [conditions, setConditions] = useState("");
  const [validationError, setValidationError] = useState("");
  const [showConfirmation, setShowConfirmation] = useState(false);

  const decisionOptions = [
    {
      value: "APPROVED",
      label: "Approve",
    },
    {
      value: "APPROVED_WITH_CONDITIONS",
      label: "Approve with conditions",
    },
    {
      value: "INFORMATION_REQUESTED",
      label: "Request more information",
    },
    {
      value: "REJECTED",
      label: "Reject",
    },
  ];

  function handleSubmit(event) {
    event.preventDefault();

    if (!reviewerName.trim() || !reviewerRole.trim()) {
      setValidationError(
        "Reviewer name and reviewer role are required.",
      );
      return;
    }

    if (!reason.trim()) {
      setValidationError(
        "Please explain the evidence and policy basis for your decision.",
      );
      return;
    }

    if (
      (decision === "APPROVED_WITH_CONDITIONS" ||
        decision === "INFORMATION_REQUESTED") &&
      !conditions.trim()
    ) {
      setValidationError(
        "Add at least one condition or required-information item.",
      );
      return;
    }

    setValidationError("");
    setShowConfirmation(true);
  }

  function confirmDecision() {
    const conditionList = conditions
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);

    setShowConfirmation(false);
    onSubmit({
      reviewer_name: reviewerName.trim(),
      reviewer_role: reviewerRole.trim(),
      decision,
      reason: reason.trim(),
      conditions: conditionList,
    });
  }

  const recommendation =
    assessment.recommendation?.decision;

  const recommendationMeta =
    RECOMMENDATION_META[recommendation] || {
      color: "#e2e8f0",
    };

  return (
    <form onSubmit={handleSubmit}>
      <h3 style={sectionHeadingStyle}>
        Human review checkpoint
      </h3>

      <div
        style={{
          padding: 14,
          marginBottom: 18,
          borderRadius: 10,
          background: "#091320",
          border: "1px solid #26364d",
        }}
      >
        <p
          style={{
            margin: 0,
            color: "#94a3b8",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          The system recommends{" "}
          <strong
            style={{
              color: recommendationMeta.color,
            }}
          >
            {formatLabel(recommendation)}
          </strong>
          . This is not a final decision. Review the evidence,
          findings and policy results before recording the human
          outcome.
        </p>
      </div>

      <label style={labelStyle}>
        Reviewer name
      </label>

      <input
        value={reviewerName}
        onChange={(event) => setReviewerName(event.target.value)}
        placeholder="e.g. Agrima Saxena"
        style={inputStyle}
      />

      <label style={labelStyle}>
        Reviewer role
      </label>

      <input
        value={reviewerRole}
        onChange={(event) => setReviewerRole(event.target.value)}
        placeholder="e.g. Security Reviewer"
        style={inputStyle}
      />

      <label style={labelStyle}>
        Decision
      </label>

      <select
        value={decision}
        onChange={(event) =>
          setDecision(event.target.value)
        }
        style={inputStyle}
      >
        {decisionOptions.map((option) => (
          <option
            key={option.value}
            value={option.value}
          >
            {option.label}
          </option>
        ))}
      </select>

      <label style={labelStyle}>
        Reason
      </label>

      <textarea
        value={reason}
        onChange={(event) =>
          setReason(event.target.value)
        }
        placeholder="Explain the evidence and policy basis for your decision."
        rows={5}
        style={{
          ...inputStyle,
          resize: "vertical",
        }}
      />

      {(
        decision === "APPROVED_WITH_CONDITIONS" ||
        decision === "INFORMATION_REQUESTED"
      ) && (
        <>
          <label style={labelStyle}>
            Conditions or required information
          </label>

          <textarea
            value={conditions}
            onChange={(event) =>
              setConditions(event.target.value)
            }
            placeholder="Enter one condition or required item per line."
            rows={5}
            style={{
              ...inputStyle,
              resize: "vertical",
            }}
          />
        </>
      )}

      {validationError && (
        <p
          style={{
            margin: "0 0 12px",
            color: "#f87171",
            fontSize: 12,
          }}
        >
          {validationError}
        </p>
      )}

      {showConfirmation && (
        <div className="review-modal-backdrop" role="presentation">
          <div className="review-modal" role="dialog" aria-modal="true" aria-labelledby="review-confirm-title">
            <h3 id="review-confirm-title">Confirm human decision</h3>
            <p><strong>Reviewer:</strong> {reviewerName} — {reviewerRole}</p>
            <p><strong>Decision:</strong> {formatLabel(decision)}</p>
            <p>This decision becomes part of the permanent audit trail and cannot be directly edited.</p>
            <div className="review-modal-actions">
              <button type="button" className="secondary" onClick={() => setShowConfirmation(false)}>
                Cancel
              </button>
              <button type="button" onClick={confirmDecision}>
                Confirm decision
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={submitting}
        style={{
          width: "100%",
          border: "none",
          borderRadius: 9,
          padding: "13px 16px",
          background: submitting
            ? "#334155"
            : "#34d399",
          color: submitting
            ? "#94a3b8"
            : "#02120d",
          fontSize: 14,
          fontWeight: 800,
          cursor: submitting
            ? "not-allowed"
            : "pointer",
        }}
      >
        {submitting
          ? "Recording decision..."
          : "Record human decision"}
      </button>
    </form>
  );
}


function CompletedDecision({ assessment }) {
  const decision = assessment.human_decision;

  if (!decision) {
    return (
      <EmptyState text="The assessment is complete, but no human decision data was returned." />
    );
  }

  const meta =
    HUMAN_DECISION_META[decision.decision] || {
      label: formatLabel(decision.decision),
      color: "#e2e8f0",
      background: "#091320",
      border: "#26364d",
    };

  return (
    <div>
      <h3 style={sectionHeadingStyle}>
        Recorded human decision
      </h3>

      <div
        style={{
          padding: 18,
          borderRadius: 12,
          background: meta.background,
          border: `1px solid ${meta.border}`,
        }}
      >
        <span
          style={{
            color: "#64748b",
            fontSize: 11,
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
          }}
        >
          Final human outcome
        </span>

        <h2
          style={{
            color: meta.color,
            margin: "8px 0 12px",
            fontSize: 22,
          }}
        >
          {meta.label}
        </h2>

        <p
          style={{
            margin: 0,
            color: "#cbd5e1",
            fontSize: 13,
            lineHeight: 1.65,
          }}
        >
          {decision.reason}
        </p>

        {decision.conditions?.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <strong
              style={{
                color: "#94a3b8",
                fontSize: 12,
              }}
            >
              Conditions or required information
            </strong>

            {decision.conditions.map((item, index) => (
              <p
                key={`${item}-${index}`}
                style={{
                  margin: "7px 0 0",
                  color: "#cbd5e1",
                  fontSize: 12,
                }}
              >
                • {item}
              </p>
            ))}
          </div>
        )}

        <p
          style={{
            margin: "16px 0 0",
            color: "#64748b",
            fontSize: 11,
          }}
        >
          Reviewer: {decision.reviewer_name || "Unknown"}
          {decision.reviewer_role ? ` — ${decision.reviewer_role}` : ""}
          {decision.decision_timestamp
            ? ` · ${new Date(decision.decision_timestamp).toLocaleString()}`
            : ""}
        </p>
      </div>
    </div>
  );
}


function EmptyState({ text }) {
  return (
    <div
      style={{
        padding: 16,
        borderRadius: 10,
        background: "#091320",
        border: "1px solid #26364d",
        color: "#64748b",
        fontSize: 13,
      }}
    >
      {text}
    </div>
  );
}


function AssessmentPage({
  vendor,
  existingAssessmentId = null,
  onBack,
}) {
  const [assessment, setAssessment] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [activeTab, setActiveTab] =
    useState("overview");

  useEffect(() => {
    let active = true;

    async function loadAssessment() {
      try {
        setLoading(true);
        setError("");

        const result = existingAssessmentId
          ? await getAssessment(existingAssessmentId)
          : await startAssessment(vendor.vendor_id);

        if (active) {
          setAssessment(result);
        }
      } catch (assessmentError) {
        console.error(assessmentError);

        if (active) {
          setError(
            existingAssessmentId
              ? "The saved assessment could not be loaded."
              : "The assessment could not be started. Confirm that the backend is running on port 8000.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadAssessment();

    return () => {
      active = false;
    };
  }, [vendor.vendor_id, existingAssessmentId]);

  async function handleReview(reviewPayload) {
    if (!assessment) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const updatedAssessment =
        await submitReview(
          assessment.assessment_id,
          reviewPayload,
        );

      setAssessment(updatedAssessment);
    } catch (reviewError) {
      console.error(reviewError);

      setError(
        "The human decision could not be recorded. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function refreshAssessment() {
    if (!assessment?.assessment_id) {
      return;
    }

    try {
      const refreshed = await getAssessment(
        assessment.assessment_id,
      );

      setAssessment(refreshed);
    } catch (refreshError) {
      console.error(refreshError);
    }
  }

  if (loading) {
    return (
      <div style={pageStyle}>
        <div
          style={{
            maxWidth: 700,
            margin: "0 auto",
            padding: "100px 24px",
            textAlign: "center",
          }}
        >
          <div className="spinner" />

          <h2
            style={{
              color: "#e2e8f0",
              marginTop: 22,
            }}
          >
            Running assessment
          </h2>

          <p
            style={{
              color: "#64748b",
              lineHeight: 1.6,
            }}
          >
            VendorGuard is extracting evidence, checking security
            risks, evaluating policy requirements and preparing a
            recommendation.
          </p>
        </div>
      </div>
    );
  }

  if (error && !assessment) {
    return (
      <div style={pageStyle}>
        <div
          style={{
            maxWidth: 760,
            margin: "0 auto",
            padding: "70px 24px",
          }}
        >
          <button
            onClick={onBack}
            style={secondaryButtonStyle}
          >
            ← Back
          </button>

          <div
            style={{
              marginTop: 22,
              padding: 18,
              borderRadius: 10,
              background: "#2b0d0d",
              border: "1px solid #dc2626",
              color: "#f87171",
            }}
          >
            {error}
          </div>
        </div>
      </div>
    );
  }

  const riskAssessment =
    assessment?.risk_assessment;

  const recommendation =
    assessment?.recommendation;

  const recommendationMeta =
    RECOMMENDATION_META[
      recommendation?.decision
    ] || {
      color: "#e2e8f0",
      background: "#091320",
      border: "#26364d",
    };

  const auditLog =
    assessment?.audit_log || [];

  const tabs = [
    {
      id: "overview",
      label: "Overview",
    },
    {
      id: "evidence",
      label: "Evidence",
    },
    {
      id: "security",
      label: "Security",
    },
    {
      id: "policy",
      label: "Policy",
    },
    {
      id: "audit",
      label: "Audit trail",
    },
    {
      id: "review",
      label:
        assessment?.status === "COMPLETE"
          ? "Decision"
          : "Review",
    },
  ];

  return (
    <div style={pageStyle}>
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 20,
          background: "#07111e",
          borderBottom: "1px solid #21334c",
        }}
      >
        <div
          style={{
            maxWidth: 1120,
            margin: "0 auto",
            padding: "16px 24px",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <button
            onClick={onBack}
            style={secondaryButtonStyle}
          >
            ← Vendors
          </button>

          <div style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                flexWrap: "wrap",
              }}
            >
              <h1
                style={{
                  margin: 0,
                  fontSize: 20,
                  color: "#f8fafc",
                }}
              >
                {vendor.name}
              </h1>

              <RiskBadge
                tier={vendor.risk_tier}
              />
            </div>

            <p
              style={{
                margin: "5px 0 0",
                color: "#64748b",
                fontSize: 11,
              }}
            >
              Assessment{" "}
              {assessment?.assessment_id}
            </p>
          </div>

          <PipelineBadge
            auditLog={auditLog}
          />

          <span
            style={{
              padding: "6px 11px",
              borderRadius: 999,
              background:
                assessment?.status === "COMPLETE"
                  ? "#0d2b1f"
                  : "#2b1f00",
              border: `1px solid ${
                assessment?.status === "COMPLETE"
                  ? "#16a34a"
                  : "#d97706"
              }`,
              color:
                assessment?.status === "COMPLETE"
                  ? "#4ade80"
                  : "#fbbf24",
              fontSize: 11,
              fontWeight: 800,
            }}
          >
            {formatLabel(
              assessment?.status,
            )}
          </span>
        </div>
      </header>

      <main
        style={{
          maxWidth: 1120,
          margin: "0 auto",
          padding: "26px 24px 70px",
        }}
      >
        {error && (
          <div
            style={{
              marginBottom: 18,
              padding: 14,
              borderRadius: 10,
              background: "#2b0d0d",
              border: "1px solid #dc2626",
              color: "#f87171",
              fontSize: 13,
            }}
          >
            {error}
          </div>
        )}

        <PipelineNotice
          auditLog={auditLog}
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "minmax(150px, 0.7fr) minmax(260px, 1.4fr) minmax(230px, 1fr)",
            gap: 16,
            marginBottom: 22,
          }}
          className="summary-grid"
        >
          <SummaryCard title="Risk score">
            <div
              style={{
                display: "flex",
                justifyContent: "center",
              }}
            >
              <ScoreCircle
                score={
                  riskAssessment?.risk_score
                }
              />
            </div>
          </SummaryCard>

          <SummaryCard title="System recommendation">
            <div
              style={{
                padding: 14,
                borderRadius: 10,
                background:
                  recommendationMeta.background,
                border: `1px solid ${recommendationMeta.border}`,
              }}
            >
              <strong
                style={{
                  color:
                    recommendationMeta.color,
                  fontSize: 18,
                }}
              >
                {formatLabel(
                  recommendation?.decision,
                )}
              </strong>

              <p
                style={{
                  margin: "9px 0 0",
                  color: "#cbd5e1",
                  fontSize: 12,
                  lineHeight: 1.6,
                }}
              >
                {recommendation?.rationale}
              </p>
            </div>

            <p
              style={{
                margin: "12px 0 0",
                color: "#64748b",
                fontSize: 11,
              }}
            >
              Confidence:{" "}
              {Math.round(
                Number(
                  recommendation?.confidence ||
                    0,
                ) * 100,
              )}
              %
            </p>
          </SummaryCard>

          <SummaryCard title="At a glance">
            <StatRow
              label="Injection blocked"
              value={
                riskAssessment
                  ?.prompt_injection_detected
                  ? "Yes"
                  : "No"
              }
              color={
                riskAssessment
                  ?.prompt_injection_detected
                  ? "#f87171"
                  : "#4ade80"
              }
            />

            <StatRow
              label="Policy violations"
              value={
                assessment?.policy_check
                  ?.violations?.length || 0
              }
              color={
                assessment?.policy_check
                  ?.violations?.length
                  ? "#fbbf24"
                  : "#4ade80"
              }
            />

            <StatRow
              label="Evidence items"
              value={
                assessment?.evidence_ledger
                  ?.items?.length || 0
              }
              color="#60a5fa"
            />

            <StatRow
              label="Human approval"
              value="Required"
              color="#a78bfa"
            />
          </SummaryCard>
        </div>

        <div
          style={{
            display: "flex",
            gap: 5,
            padding: 5,
            marginBottom: 16,
            overflowX: "auto",
            background: "#0f1d30",
            border: "1px solid #21334c",
            borderRadius: 11,
          }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() =>
                setActiveTab(tab.id)
              }
              style={{
                minWidth: 110,
                flex: 1,
                padding: "9px 11px",
                border: "none",
                borderRadius: 8,
                background:
                  activeTab === tab.id
                    ? "#24344d"
                    : "transparent",
                color:
                  activeTab === tab.id
                    ? "#f8fafc"
                    : "#64748b",
                fontWeight:
                  activeTab === tab.id
                    ? 800
                    : 500,
                fontSize: 12,
                cursor: "pointer",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <section
          style={{
            background: "#0f1d30",
            border: "1px solid #21334c",
            borderRadius: 14,
            padding: 22,
          }}
        >
          {activeTab === "overview" && (
            <div>
              <h3 style={sectionHeadingStyle}>
                Assessment summary
              </h3>

              <p
                style={{
                  color: "#cbd5e1",
                  fontSize: 13,
                  lineHeight: 1.7,
                }}
              >
                {recommendation?.rationale}
              </p>

              {recommendation
                ?.missing_evidence?.length >
                0 && (
                <>
                  <h4
                    style={{
                      color: "#fbbf24",
                      margin: "24px 0 10px",
                    }}
                  >
                    Missing evidence
                  </h4>

                  {recommendation.missing_evidence.map(
                    (item, index) => (
                      <p
                        key={`${item}-${index}`}
                        style={{
                          color: "#d6a84b",
                          fontSize: 12,
                        }}
                      >
                        • {item}
                      </p>
                    ),
                  )}
                </>
              )}

              <button
                onClick={refreshAssessment}
                style={{
                  ...secondaryButtonStyle,
                  marginTop: 20,
                }}
              >
                Refresh status
              </button>
            </div>
          )}

          {activeTab === "evidence" && (
            <EvidencePanel
              ledger={
                assessment.evidence_ledger
              }
            />
          )}

          {activeTab === "security" && (
            <SecurityPanel
              riskAssessment={
                riskAssessment
              }
            />
          )}

          {activeTab === "policy" && (
            <PolicyPanel
              policyCheck={
                assessment.policy_check
              }
            />
          )}

          {activeTab === "audit" && (
            <AuditTimeline
              auditLog={auditLog}
            />
          )}

          {activeTab === "review" &&
            (assessment.status ===
            "COMPLETE" ? (
              <CompletedDecision
                assessment={assessment}
              />
            ) : (
              <HumanReviewPanel
                assessment={assessment}
                submitting={submitting}
                onSubmit={handleReview}
              />
            ))}
        </section>
      </main>
    </div>
  );
}

export default function App() {
  const [vendors, setVendors] = useState([]);
  const [vendorsLoading, setVendorsLoading] = useState(true);
  const [view, setView] = useState("home");
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState(null);
  const [startingVendorId, setStartingVendorId] = useState("");

  useEffect(() => {
    async function loadVendors() {
      try {
        setVendors(await getVendors());
      } catch (error) {
        console.error("Could not load vendors:", error);
        setVendors([]);
      } finally {
        setVendorsLoading(false);
      }
    }
    loadVendors();
  }, []);

  function goHome() {
    setView("home");
    setSelectedVendor(null);
    setSelectedAssessmentId(null);
    setStartingVendorId("");
  }

  function handleVendorSelection(vendor) {
    setStartingVendorId(vendor.vendor_id);
    setSelectedVendor(vendor);
    setSelectedAssessmentId(null);
    setView("assessment");
    window.setTimeout(() => setStartingVendorId(""), 500);
  }

  function handleOpenAssessment(summary) {
    setSelectedVendor({
      vendor_id: summary.vendor_id,
      name: summary.vendor_name,
      risk_tier: summary.risk_tier,
    });
    setSelectedAssessmentId(summary.assessment_id);
    setView("assessment");
  }

  if (view === "history") {
    return (
      <AssessmentHistory
        onBack={goHome}
        onOpenAssessment={handleOpenAssessment}
      />
    );
  }

  if (view === "assessment" && selectedVendor) {
    return (
      <AssessmentPage
        vendor={selectedVendor}
        existingAssessmentId={selectedAssessmentId}
        onBack={() => setView("history")}
      />
    );
  }

  return (
    <HomePage
      vendors={vendors}
      loading={vendorsLoading}
      startingVendorId={startingVendorId}
      onSelect={handleVendorSelection}
      onOpenHistory={() => setView("history")}
    />
  );
}


const pageStyle = {
  minHeight: "100vh",
  background: "#06101c",
  color: "#e2e8f0",
};


const sectionHeadingStyle = {
  color: "#f8fafc",
  margin: "0 0 18px",
  fontSize: 18,
};


const labelStyle = {
  display: "block",
  color: "#cbd5e1",
  fontSize: 12,
  fontWeight: 800,
  margin: "0 0 7px",
};


const inputStyle = {
  width: "100%",
  boxSizing: "border-box",
  marginBottom: 16,
  padding: "12px 13px",
  borderRadius: 9,
  border: "1px solid #334155",
  background: "#091320",
  color: "#f8fafc",
  fontFamily: "inherit",
  fontSize: 13,
};


const secondaryButtonStyle = {
  padding: "8px 12px",
  borderRadius: 8,
  border: "1px solid #334155",
  background: "#0f1d30",
  color: "#cbd5e1",
  cursor: "pointer",
  fontWeight: 700,
};
