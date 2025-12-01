"""Subagents for the lead  pipeline."""

# Import the actual agent instance defined in input_agent/agent.py
from .consumption_data_agent.agent import consumption_data_agent

# Import the actual agent instance defined in latlong_agent/agent.py
from .weather_data_agent.agent import weather_data_agent
__all__ = ["consumption_data_agent", "weather_data_agent"]
