from google.adk.agents import ParallelAgent
#from .sub_agents.input_agent.agent import input_agent as InputAgentInstance
#from .sub_agents.latlong_agent.agent import latlong_agent as LatLongAgentInstance
from .sub_agents import consumption_data_agent, weather_data_agent
import logging

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)
log.info("Instantiated baseline_data_agent_parallel")

baseline_data_agent_parallel = ParallelAgent(
    name="baseline_data_agent_parallel",
    # https://ai.google.dev/gemini-api/docs/models
 #  model="gemini-2.5-flash",
    description="Data Baseline agent that "\
    "1) Fetches Energy Data using latitude and longitude of city"\
    "2) Generates Historic Energy consumption data for the city",
    sub_agents=[consumption_data_agent, weather_data_agent]     
)
#root_agent = baseline_data_agent_parallel