from google.adk.agents import SequentialAgent
import pandas as pd
import numpy as np
import json
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.plugins.logging_plugin import LoggingPlugin

from .sub_agents import input_agent
from .sub_agents import latlong_agent
from .sub_agents.regression_agent.agent import regression_agent
from .sub_agents.prediction_agent.agent import prediction_agent
from .sub_agents.baseline_data_agent_parallel.agent import baseline_data_agent_parallel
from config.settings import SHARED_RETRY_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Instantiated baseline_agent_sequential")

baseline_agent_sequential = SequentialAgent(
    name="baseline_agent_sequential",
    # https://ai.google.dev/gemini-api/docs/models
 #  model="gemini-2.5-flash",
    description="Energy Baseline sequential agent that runs the following sequential agents to perform regression analysis "\
    "1)Input Agent that collects user info (name, city, dates)"\
        "Provides latitude and longitude for the city",
    #"2)Provide latitude and longitude of the city in strict JSON format as:"\
    #    "{\"geolocation\": {\"latitude\": float, \"longitude\": float}}",
    # 3) Generate sample energy consumption data and fetch weather data for the given date range in strict JSON format.
    #     Save the data in memory
    # 4) Fit regression model (model training) and produce tomorrow's energy consumption data (model testing).
    #     Save the regression equation and metrics in memory.
    
    #sub_agents=[greeting_agent, latlong_agent],
    sub_agents=[input_agent, latlong_agent, baseline_data_agent_parallel,regression_agent,prediction_agent]     
)
# root_agent = baseline_agent_sequential

# def run_multi_agents_baseline_workflow():
#     """
#     Runs the Multiple Regression Agent followed by the Prediction Agent in a single session.
#     """
#     print("🚀 Starting Multiple Regression Agent Workflow...")
    
#     session_service = InMemorySessionService()
#     runner = Runner(
#         agent=regression_agent, 
#         app_name="multiple_regression_prediction_app",
#         session_service=session_service,
#         plugins=[LoggingPlugin()]
#     )
    
#     USER_ID = "multiple_workflow_user"
#     session = runner.create_session(user_id=USER_ID)
    
#     # --- Step 1: Agent 1- Input agent saves use input ---
    
#     input_prompt = (
#         f"Greet user '{USER_ID}' and ask user to  provide name , city and baseline start and end date. "
#     )
#     print("\n" + "="*70)
#     print("▶️ AGENT 1: Taking user input...")
#     response_1_text = ""
#     for event in runner.stream_query(
#         user_id=USER_ID,
#         session_id=session.id,
#         message=input_prompt,
#         agent=input_agent
#     ):
#        if event.text:
#             response_1_text += event.text
#             logger.info(event.text)

            

#     print(f"\n✅ Agent 1 Response (User Inputs):\n{response_1_text.strip()}")
    
# # --- Step 2: Agent 2- LatLong agent finds out latitude and longitude of the city from the user data ---

#     latlong_prompt = (
#         f" Find out latitude and longitude of city from user input received by input_agent. "
#     )
#     print("\n" + "="*70)
#     print("▶️ AGENT 2: Finding out latitude and longitude...")
#     response_2_text = ""
#     for event in runner.stream_query(
#         user_id=USER_ID,
#         session_id=session.id,
#         message=latlong_prompt,
#         agent=latlong_agent
#     ):
#        if event.text:
#             response_2_text += event.text
#             logger.info(event.text)
#             print(event.text, end="", flush=True)

#     print(f"\n✅ Agent 2 Response (latitude and longitude):\n{response_2_text.strip()}")
# # --- Step 3: Agent 3- Baseline data generator agent ---

#     baseline_data_prompt = (f" Fetch weather data, Generate consumption data in fixed JSON format.")
#     print("\n" + "="*70)
#     print("▶️ AGENT 3: Generating weather and consumption data...")
#     response_3_text = ""
#     for event in runner.stream_query(
#         user_id=USER_ID,
#         session_id=session.id,
#         message=baseline_data_prompt,
#         agent=baseline_data_agent_parallel
#     ):
#        if event.text:
#             response_3_text += event.text
#             logger.info(event.text)
#             print(event.text, end="", flush=True)

#     print(f"\n✅ Agent 3 Response (Regression data generated):\n{response_3_text.strip()}")
# # --- Step 4: Agent 4- Regression agent ---
#     regression_prompt = "Now, perform the multiple linear regression using the data provided in the previous steps."
#     print("\n" + "="*70)
#     print("▶️ AGENT 4: Running Multiple Regression (C ~ T + H + D)...")
#     response_4_text = ""
#     for event in runner.stream_query(
#     user_id=USER_ID, 
#     session_id=session.id, 
#     message=regression_prompt, 
#     agent=regression_agent
#     ):
#         if event.text:
#             logger.info(event.text)
#             response_4_text += event.text
    
#     print(f"\n✅ Agent 1 Response (Parameters in Context):\n{response_4_text.strip()}")

# # --- Step 5: Agent 5- Prediction agent ---
#     prediction_prompt = "Using the resulting equation, predict consumption for the new weather data."
    
#     print("\n" + "="*70)
#     print("▶️ AGENT 5: Running Prediction...")
    
#     response_5_text = ""
#     for event in runner.stream_query(
#         user_id=USER_ID, 
#         session_id=session.id, 
#         message=prediction_prompt,
#         agent=prediction_agent
#     ):
#         if event.text:
#             response_5_text += event.text
#             logger.info(event.text)
            
#     print(f"\n✅ Agent 5 Final Prediction:\n{response_4_text.strip()}")
#     print("="*70)
# if __name__ == '__main__':
#     # You will need to install: pip install google-adk pandas numpy pydantic
#     # And ensure your GOOGLE_API_KEY environment variable is set.
#     run_multi_agents_baseline_workflow()
