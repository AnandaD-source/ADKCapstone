from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, FunctionTool
from google.adk.models.google_llm import Gemini
import logging
from typing import Any, Dict, List
from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.invocation_context import InvocationContext
from pydantic import BaseModel, Field
from config.settings import SHARED_RETRY_CONFIG
from .sub_agents import latlong_agent

logger = logging.getLogger(__name__)

# Define the expected date format if known (e.g., 'YYYY-MM-DD')
# Adjust this format string (%Y-%m-%d) to match your input date strings
DATE_FORMAT = "%Y-%m-%d"

def save_userinfo(
    tool_context: ToolContext, 
    user_name: str, 
    city: str, 
    dates: List[str],
    latitude: float,    # Expects Python float
    longitude: float    # Expects Python float
) -> Dict[str, Any]:
    user_info = {
        "name": user_name,
        "dates_provided": dates,
        "baseline_from_date": None,
        "baseline_end_date": None,
    }
    if len(dates) == 2:
        try:
            # 1. Convert string dates to datetime objects for reliable comparison
            date_objects = [datetime.strptime(d, DATE_FORMAT).date() for d in dates]
            
            # 2. Sort the dates (sorts in ascending order by default)
            date_objects.sort()
            
            # 3. Assign the sorted dates back to the dictionary keys (optional: convert back to string)
            user_info["baseline_from_date"] = date_objects[0].strftime(DATE_FORMAT)
            user_info["baseline_end_date"] = date_objects[1].strftime(DATE_FORMAT)
            logger.info(f"Assigned baseline dates: From {user_info['baseline_from_date']} to {user_info['baseline_end_date']}")
            
        except ValueError as e:
            logger.error(f"Error parsing dates with format {DATE_FORMAT}: {e}")
            user_info["error"] = "Invalid date format provided."
    else:
        logger.info(f"Did not assign baseline dates: Expected 2 dates, but got {len(dates)}")

    # Save the information to the agent's state using tool_context
    tool_context.state["user:user_data"] = user_info
    tool_context.state["city"] = city
    tool_context.state["baseline_from_date"] = user_info["baseline_from_date"]
    tool_context.state["baseline_end_date"] = user_info["baseline_end_date"]    
    logger.info(f"Assigned baseline dates: From {user_info['baseline_from_date']} todate {user_info['baseline_end_date']}")
    tool_context.state["latitude"] = latitude        
    tool_context.state["longitude"] = longitude
    logger.info(f"Saved user info to state: {city}")
    return {"status": "success", "user_info_saved": user_info}
# The latlong_agent is a specialized agent designed to find coordinates and output JSON.
root_agent = Agent(
    name="InputAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="Input and Geo-location Agent",
    instruction="""
    You are a helpful energy baseline assistant. Greet the user and ask for their name, city, 
    and two dates (start and end) for baseline creation in YYYY-MM-DD format.
    
    PROCESS THE INPUT IN TWO STEPS:
    1. **FIRST**, use the **get_city_coordinates** tool (which internally calls the LatLong Agent) 
       with the city provided by the user to find the latitude and longitude.
    2. **NEXT**, use the **save_userinfo** tool to save the user's name, city, the two dates, 
       AND the retrieved latitude and longitude to the session state.
    """,
    # Include both the AgentTool wrapper and your custom function tool
    tools=[FunctionTool(save_userinfo),AgentTool(latlong_agent)],
    )