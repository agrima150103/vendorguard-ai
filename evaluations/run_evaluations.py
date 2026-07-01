from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.repositories.assessment_repository import init_db
from app.services.assessment_service import start_assessment


def main():
    init_db()
    results = []
    for path in sorted((ROOT / "evaluations" / "scenarios").glob("*.json")):
        expected = json.loads(path.read_text(encoding="utf-8"))
        assessment = start_assessment(expected["vendor_id"])
        checks = {
            "recommendation": assessment.recommendation.decision.value == expected["expected_recommendation"],
            "prompt_injection": assessment.risk_assessment.prompt_injection_detected == expected["prompt_injection"],
            "human_gate": (assessment.status.value == "AWAITING_HUMAN_REVIEW") == expected["human_gate"],
        }
        results.append({
            "scenario_id": expected["scenario_id"],
            "passed": all(checks.values()),
            "checks": checks,
        })

    print(json.dumps(results, indent=2))
    failed = [item for item in results if not item["passed"]]
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
