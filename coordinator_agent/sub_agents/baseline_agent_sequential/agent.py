from google.adk.agents import SequentialAgent
import pandas as pd
import numpy as np
import json
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.plugins.logging_plugin import LoggingPlugin

#from .sub_agents import input_agent
#from .sub_agents import latlong_agent
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
    name="AnalyticalCoreAgentSequential",
    # https://ai.google.dev/gemini-api/docs/models
 #  model="gemini-2.5-flash",
    description="Energy Baseline sequential agent that runs the following sequential agents to perform regression analysis "\
    "1)Input Agent that collects user info (name, city, dates)"\
        "Provides latitude and longitude for the city"
    "2)Provide latitude and longitude of the city in strict JSON format"\
    "3) Generate sample energy consumption data and fetch weather data for the given date range in strict JSON format."\
    "4) Fit regression model (model training) and produce tomorrow's energy consumption data (model testing)."\
    "5) Test the regression equation by running prediction on a sample data point.",
    sub_agents=[baseline_data_agent_parallel,regression_agent,prediction_agent] 
)
