"""
Compatibility entry point for Google ADK.

The actual multi-agent workflow is defined in root_agent.py.
"""

from app.agents.root_agent import root_agent


__all__ = ["root_agent"]