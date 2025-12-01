"""Subagents for the lead  pipeline."""

# Import the actual agent instance defined in pipeline_agent/agent.py
#from .pipeline_agent.agent import pipeline_agent

# Import the actual agent instance defined in latlong_agent/agent.py
from .latlong_agent.agent import latlong_agent

# Explicitly export the imported agent instances so linters recognize they're used
__all__ = ["pipeline_agent", "latlong_agent"]
