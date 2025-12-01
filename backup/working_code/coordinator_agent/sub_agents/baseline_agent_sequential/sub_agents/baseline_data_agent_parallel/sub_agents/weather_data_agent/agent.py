from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import logging
import requests
from typing import Any, Dict, List
from datetime import date # Changed from datetime imported date directly
from pydantic import BaseModel, Field
from config.settings import SHARED_RETRY_CONFIG 


# Assuming this log object exists in your file
log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Output Schemas (Simplified)
# -------------------------------------------------------------------

class DailyWeatherRecord(BaseModel):
    # Renamed record_date to date to match API output slightly better, adjust as needed
    date: str 
    temperature: float = Field(..., description="Mean daily temperature in Celsius.")
    humidity: float = Field(..., description="Mean daily relative humidity percentage.")
    dewpoint: float = Field(..., description="Mean daily dew point in Celsius.")

# This is the schema the agent MUST return a dictionary matching this structure
class MultiDayWeatherData(BaseModel):
    # Renamed the field to match what the function will now return
    daily_records: List[DailyWeatherRecord] = Field(..., description="A list of daily weather records.")

# -------------------------------------------------------------------
def get_weather_daily(geo_location:Dict[str, float], start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Fetch daily weather data and format it to match the MultiDayWeatherData schema.
    """

    try:
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": geo_location.get("latitude"),
            "longitude": geo_location.get("longitude"),
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_mean",
                "relative_humidity_2m_mean",
                "dew_point_2m_mean"
            ],
            "timezone": "auto"
        }
        log.info(f"Fetching weather data with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract arrays
        dates = data["daily"]["time"]
        temps = data["daily"]["temperature_2m_mean"]
        hums = data["daily"]["relative_humidity_2m_mean"]
        dews = data["daily"]["dew_point_2m_mean"]

        weather_records = []
        for d, t, h, dp in zip(dates, temps, hums, dews):
            record = DailyWeatherRecord(
                date=d,
                temperature=t,
                humidity=h,
                dewpoint=dp
            )
            weather_records.append(record.model_dump()) # Convert Pydantic object back to a dictionary

        
        return {
            "daily_records": weather_records
        }

    except Exception as e:
        log.error(f"Error fetching weather data: {e}")
        return {
            "daily_records": [] # Return an empty list if schema must be matched
        }


# -------------------------------------------------------------------
# Agent Definition
# -------------------------------------------------------------------

weather_data_agent = Agent(
    name="weather_data_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model= Gemini (model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="An agent that provides historic weather data of a location",
    instruction="""
    Provide weather data points for city for the given date range. 
    You MUST read the  dates baseline start date from session state key baseline_from_date 
    and baseline end date from state key baseline_end_date before proceeding.
    The output must conform strictly to the provided JSON schema.
    Generate 1 record per day. weather data points include date, temperature, relative humidity, and dew point.
    To fetch the weather data,use get_weather_daily tool.
    The tool returns a dictionary with keys 'status' and either 'weather_data' (on success) or 'message' (on error).
    No explaination required. Do not ask any quetsions
    """,
      tools=[get_weather_daily],
      output_schema=MultiDayWeatherData,
      output_key="weather_data",
)
