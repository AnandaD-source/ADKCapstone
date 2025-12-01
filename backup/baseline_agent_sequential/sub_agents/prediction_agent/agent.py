from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.code_executors import BuiltInCodeExecutor
import json
from typing import Dict, Any, List
from config.settings import SHARED_RETRY_CONFIG
import logging
log = logging.getLogger(__name__)
# New weather data for which Agent 2 will make a prediction
NEW_WEATHER_DATA = {
    "temperature": 21.5,  # New Temperature
    "humidity": 70.0, # New Humidity
    "dewpoint": 20  # New Dewpoint
}
prediction_agent = Agent(
    name="Prediction_Agent",
    model= Gemini (model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="Agent that reads multiple regression parameters from history and makes a prediction.",
    instruction=f"""
    Your goal is to predict energy consumption for the new weather data: {json.dumps(NEW_WEATHER_DATA)}.
    
    1. **Examine the conversation history:** Look at the preceding message from the 'Regression_Agent'.
    2. **Extract parameters:** Use the BuiltInCodeExecutor and string parsing to find the numerical values 
       sandwiched between the [INTERCEPT_START], [TEMP_COEF_START], [HUMIDITY_COEF_START], and [DEWPOINT_COEF_START] tags.
    3. **Perform Prediction:** Use the extracted intercept and coefficients along with the new weather data 
       (T={NEW_WEATHER_DATA['temperature']}, H={NEW_WEATHER_DATA['humidity']}, D={NEW_WEATHER_DATA['dewpoint']})
       to calculate the predicted consumption.
    4. **Respond:** State the final predicted consumption value clearly.
    """,
    code_executor=BuiltInCodeExecutor(),
)
