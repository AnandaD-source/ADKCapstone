from config.settings import SHARED_RETRY_CONFIG
from .sub_agents import baseline_agent_sequential
from .sub_agents import input_agent
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.plugins.logging_plugin import LoggingPlugin

root_agent = Agent(
    name="file_io_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    description="Input and Geo-location Agent",
    instruction="""
    You are a helpful filing assistant. Perform the following tasks:
    1. Read file inputs from the user.
    2 Save weather data files to the appropriate directories.
    3.Save energy data files to the appropriate directories.


    For performing these tasks, use the following sub-agents in sequence:
    1. Input Agent- Use this agent to greet the user to collect and save user data viz name, city, 
    and two dates (baseline start and baseline end date) for baseline creation in YYYY-MM-DD format.
    2.Analytical Core agent - Use this agent to perform regression analysis for energy baseline creation.
    
    """,
    # Include both the AgentTool wrapper and your custom function tool
    sub_agents=[input_agent, baseline_agent_sequential]
    )