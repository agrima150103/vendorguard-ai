# Low-Level Design

## Assessment state transitions

PENDING → EXTRACTING_EVIDENCE → ANALYSING_RISK → CHECKING_POLICY →
GENERATING_RECOMMENDATION → AWAITING_HUMAN_REVIEW → COMPLETE

`FAILED` is available for controlled terminal failures.

## Invariants

- `AssessmentRecommendation.human_approval_required` can only be `true`.
- A review is accepted only in `AWAITING_HUMAN_REVIEW`.
- A completed assessment cannot be reviewed again.
- Prompt-injection content is stored as evidence but never executed.
