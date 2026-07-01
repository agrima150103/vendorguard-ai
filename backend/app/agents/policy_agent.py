"""
VendorGuard AI — ADK Policy Agent

Uses an MCP stdio server to retrieve and evaluate governed policy rules.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters


MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Current file:
# project/backend/app/agents/policy_agent.py
#
# parents[0] = agents
# parents[1] = app
# parents[2] = backend
# parents[3] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MCP_SERVER_PATH = PROJECT_ROOT / "mcp_server" / "server.py"


POLICY_AGENT_INSTRUCTION = """
You are the Policy Agent for VendorGuard AI.

You receive:

- evidence results in {evidence_output};
- risk and security results in {risk_output};
- original vendor metadata from the initial user message.

You must use the VendorGuard MCP policy tools.

Required tool sequence:

1. Call get_policy_rules using the vendor's risk tier.
2. Call get_required_documents using the vendor's risk tier
   and service type.
3. Call check_policy_compliance using facts extracted by earlier agents.
4. Call get_risk_thresholds before producing the policy verdict.

Rules:

- Never invent policy rules.
- Report exact rule identifiers returned by MCP.
- Preserve rule severity.
- Do not treat a missing claim as proof of compliance.
- Do not make a binding human decision.
- HITL-001 must always remain applicable.
- If an MCP tool fails, state that policy verification is incomplete.

Finish with exactly this format:

POLICY_SUMMARY
vendor_id: <vendor id>
risk_tier: <LOW, MEDIUM or HIGH>
total_rules_checked: <number>
violations:
  - rule_id: <rule id>
    severity: <critical, high, medium or low>
    description: <description>
passed_rules: <comma-separated rule ids or none>
missing_mandatory_documents: <comma-separated documents or none>
policy_verdict: <APPROVE, APPROVE_WITH_CONDITIONS,
REQUEST_MORE_INFORMATION, ESCALATE_TO_HUMAN or REJECT>
END_POLICY_SUMMARY
"""


def create_policy_agent() -> LlmAgent:
    """
    Create the Policy Agent and connect it to the MCP policy server.

    The MCP server runs as a Python subprocess using stdio transport.
    """

    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(MCP_SERVER_PATH)],
            ),
            timeout=30,
        ),
        tool_filter=[
            "get_policy_rules",
            "get_required_documents",
            "check_policy_compliance",
            "get_risk_thresholds",
        ],
    )

    return LlmAgent(
        name="policy_agent",
        model=MODEL,
        description=(
            "Checks vendor evidence against governed onboarding "
            "policy through MCP tools."
        ),
        instruction=POLICY_AGENT_INSTRUCTION,
        tools=[mcp_toolset],
        output_key="policy_output",
    )