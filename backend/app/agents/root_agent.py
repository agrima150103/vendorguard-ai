"""
VendorGuard AI — Root ADK Sequential Agent

The workflow order is deterministic:

Evidence Agent
→ Risk and Security Agent
→ Policy Agent using MCP
→ Decision and Report Agent
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent

from app.agents.decision_agent import create_decision_agent
from app.agents.evidence_agent import create_evidence_agent
from app.agents.policy_agent import create_policy_agent
from app.agents.risk_security_agent import (
    create_risk_security_agent,
)


def create_assessment_agent() -> SequentialAgent:
    """Create the complete governed VendorGuard agent pipeline."""

    return SequentialAgent(
        name="vendorguard_assessment_orchestrator",
        description=(
            "Runs evidence extraction, security analysis, MCP policy "
            "checking and recommendation generation in a fixed order."
        ),
        sub_agents=[
            create_evidence_agent(),
            create_risk_security_agent(),
            create_policy_agent(),
            create_decision_agent(),
        ],
    )


# ADK discovers the application through this exported root_agent variable.
root_agent = create_assessment_agent()