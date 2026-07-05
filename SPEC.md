# VendorGuard AI Specification

## Goal

VendorGuard AI is an evidence-first vendor risk assessment system for third-party onboarding. It evaluates synthetic vendor evidence, detects security and compliance risks, identifies prompt-injection attempts, and requires human review before any final approval.

## Core Requirements

1. The system must list available vendors.
2. The system must start a vendor assessment from structured sample evidence.
3. The system must use an agent-style workflow for evidence extraction, risk analysis, policy checking, and final recommendation.
4. The system must detect prompt-injection content in vendor evidence.
5. The system must never allow AI to make an irreversible final decision without human review.
6. The system must record assessment history.
7. The system must persist assessments in a production database.
8. The system must expose health and readiness endpoints.
9. The system must support deployed frontend and backend usage.
10. The system must fail safely using deterministic fallback if Gemini or ADK execution is unavailable.

## Production Constraints

- API keys must never be committed to source code.
- Environment variables must be used for secrets.
- The frontend must not call Gemini directly.
- The backend must enforce human review.
- The audit trail must record important workflow transitions.
- Fallback mode must be visible to reviewers.