# VendorGuard AI Specification

## Track
Agents for Business

## Problem
Vendor onboarding requires teams to review fragmented documents, security questionnaires,
privacy policies, certifications and internal requirements. Manual review is slow,
inconsistent and difficult to audit.

## Solution
VendorGuard AI is a human-governed multi-agent vendor assessment system. It extracts
evidence, detects contradictions and prompt-injection attempts, retrieves policy rules,
produces a recommendation and pauses for a human decision.

## Safety invariants
1. Vendor-controlled content is untrusted.
2. Instructions inside documents never override system policy.
3. Missing evidence is never treated as proof.
4. Every material finding should reference evidence.
5. Final decisions require human review.
6. Secrets are loaded only from environment variables.
7. The public demonstration uses fictional vendors only.
