from __future__ import annotations

import json
from pathlib import Path


POLICY_PATH = Path(__file__).resolve().parents[3] / "mcp_server" / "policies.json"


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def applicable_rules(risk_tier: str, service_type: str) -> list[dict]:
    policy = load_policy()
    rules = []
    for rule in policy["rules"]:
        tiers = rule.get("risk_tiers", ["LOW", "MEDIUM", "HIGH"])
        if risk_tier in tiers:
            rules.append(rule)
    return rules
