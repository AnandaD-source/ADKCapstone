from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
import logging
from typing import Any, Dict, List
from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.invocation_context import InvocationContext
from pydantic import BaseModel, Field
from config.settings import SHARED_RETRY_CONFIG 

logger = logging.getLogger(__name__)

# Define the expected date format if known (e.g., 'YYYY-MM-DD')
# Adjust this format string (%Y-%m-%d) to match your input date strings
DATE_FORMAT = "%Y-%m-%d"

class location(BaseModel):
    city: str = Field(..., description="Name of the city")  

def save_userinfo(
    tool_context: ToolContext, user_name: str, city: str, dates: List[str]
) -> Dict[str, Any]:
    """
    Saves user information and assigns baseline_from/end_date if exactly two dates are provided.
    """
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
    logger.info(f"Saved user info to state: {city}")
    return {"status": "success", "user_info_saved": user_info}

# Reuse the same logger instance (or define it here if in a separate file)
#logger = logging.getLogger(__name__)
#DATE_FORMAT = "%Y-%m-%d"
#MEMORY_KEY = "persistent_user_data" # A constant key for storage

# def save_userinfo_persistent(
#     context: InvocationContext, # Parameter name changed to reflect type
#     user_name: str, 
#     city: str, 
#     dates: List[str]
# ) -> Dict[str, Any]:
#     """
#     Saves user information persistently using the Memory Service.
#     """
#     user_info = {
#         "name": user_name,
#         "city": city,
#         "dates_provided": dates,
#         "baseline_from_date": None,
#         "baseline_end_date": None,
#     }
#     if len(dates) == 2:
#         try:
#             # 1. Convert string dates to datetime objects for reliable comparison
#             date_objects = [datetime.strptime(d, DATE_FORMAT).date() for d in dates]
            
#             # 2. Sort the dates (sorts in ascending order by default)
#             date_objects.sort()
            
#             # 3. Assign the sorted dates back to the dictionary keys (optional: convert back to string)
#             user_info["baseline_from_date"] = date_objects[0].strftime(DATE_FORMAT)
#             user_info["baseline_end_date"] = date_objects[1].strftime(DATE_FORMAT)
#             logger.info(f"Assigned baseline dates: From {user_info['baseline_from_date']} to {user_info['baseline_end_date']}")
            
#         except ValueError as e:
#             logger.error(f"Error parsing dates with format {DATE_FORMAT}: {e}")
#             user_info["error"] = "Invalid date format provided."
#     else:
#         logger.info(f"Did not assign baseline dates: Expected 2 dates, but got {len(dates)}")
#     context.memory.set(MEMORY_KEY, user_info)
    
#     logger.info(f"Saved user info persistently to Memory: {user_info}")

#     return {"status": "success", "user_info_saved": user_info}


# def get_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
#     """
#     Retrieves saved user information, including baseline dates, from the session state.
#     """
#     user_info: Optional[Dict[str, Any]] = tool_context.state.get("user_data")

#     if user_info:
#         logger.info(f"Retrieved user info from state: {user_info}")
#         return {
#             "status": "success",
#             "user_data": user_info,
#             "message": "User information retrieved successfully."
#         }
#     else:
#         logger.warning("Attempted to retrieve user info, but none was found in state.")
#         return {
#             "status": "not found",
#             "message": "No user information found in the current session state."
#         }

input_agent = Agent(
    name="InputAgent",
    # https://ai.google.dev/gemini-api/docs/models
    model= Gemini (model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="Input",
    instruction="""
    Save following inputs have been provided  1.user's name, 2.city 3. baseline start dates 4.baseline end date. 
    Dates should be saved in the YYYY-MM-DD format.
    Make fuzzy match to accept city name even with minor typos.
    Use save_userinfo tool to store the user information including baseline_from and baseline_end dates in the agent's state.
    """,
    tools=[save_userinfo],
    output_schema=location, 
    output_key="city_output",
)
