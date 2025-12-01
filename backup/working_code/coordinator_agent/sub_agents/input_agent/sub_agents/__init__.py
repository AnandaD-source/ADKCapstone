"""Subagents for the lead  pipeline."""
from .latlong_agent.agent import latlong_agent

# Explicitly export the imported agent instances so linters recognize they're used
__all__ = ["latlong_agent"]
