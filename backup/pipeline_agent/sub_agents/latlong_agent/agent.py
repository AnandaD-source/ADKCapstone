from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import logging
from typing import Any, Dict, List
from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel, Field
from config.settings import SHARED_RETRY_CONFIG 
log = logging.getLogger(__name__)

class CityGeoLocationResponse(BaseModel):
    """
    A single Pydantic model combining city geolocation latitude and longitude fields.
    """
    latitude: float = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="Geographic coordinate latitude ranging from -90 to 90 degrees.",
        example=37.7749
    )
    longitude: float = Field(
        ..., 
        ge=-180, 
        le=180, 
        description="Geographic coordinate longitude ranging from -180 to 180 degrees.",
        example=-122.4194
    )

# The latlong_agent is a specialized agent designed to find coordinates and output JSON.
latlong_agent = Agent(
    name="LatLongAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="Tool to find latitude and longitude of a city and return strict JSON.",
    instruction="""
    You are a helpful assistant that provides latitude and longitude of a given city.
    You MUST output the result in strict JSON format as: {"latitude": float, "longitude": float}
    """,
    output_schema=CityGeoLocationResponse, # Ensure this schema is used
    output_key="geo_location",
)
from google.adk.tools.agent_tool import AgentTool

# # 1. Create the AgentTool wrapper
# latlong_agent_tool = AgentTool(
#     agent=latlong_agent,
#     name="get_city_coordinates",
#     description="Tool to retrieve the geographical coordinates (latitude and longitude) for a specified city name."
#     # The arguments the LLM sees are derived from the tool agent's initial prompt arguments.
# )
