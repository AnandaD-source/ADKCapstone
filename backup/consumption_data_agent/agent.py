import asyncio
import logging
import re
from datetime import date, datetime, timedelta
from typing import List, Optional

from dateutil.parser import parse, ParserError
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

REQUIRED_DURATION_DAYS = 15


# -------------------------------------------------------------------
# Callback: Validate Past Dates Exactly X Days Apart
# -------------------------------------------------------------------
def date_check_before_before_model_call(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:

    log.info(f"Callback triggered for agent: {callback_context.agent_name}")

    last_msg = ""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            last_msg = llm_request.contents[-1].parts[0].text

    log.info(f"User message: {last_msg}")

    def is_past(d: date) -> bool:
        return d < datetime.now().date()

    def extract_past_dates(text: str) -> list[date]:
        patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{1,2} [A-Za-z]+ \d{4}",
            r"[A-Za-z]+ \d{1,2}(?:,\s*)?\d{4}",
            r"\d{1,2}-[A-Za-z]+-\d{4}"
        ]

        found = set()
        for p in patterns:
            for m in re.findall(p, text):
                try:
                    d = parse(m, fuzzy=True).date()
                    if is_past(d):
                        found.add(d)
                except (ParserError, ValueError, OverflowError):
                    continue
        return list(found)

    dates = extract_past_dates(last_msg)
    log.info(f"Extracted past dates: {dates}")
    log.info(f"Number of past dates extracted: {len(dates)}")

    if len(dates) == 2:
        d1, d2 = sorted(dates)
        log.info(f"Checking date difference between {d1} and {d2} d2-d1 = {d2 - d1}") 
        if (d2 - d1) == timedelta(days=REQUIRED_DURATION_DAYS):
            log.info("Date validation passed → Allowing model call")
            return None

    log.warning("Date validation failed → Blocking model call")
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(
                text=f"LLM call blocked. You must provide exactly two past dates {REQUIRED_DURATION_DAYS} days apart."
            )],
        )
    )


# -------------------------------------------------------------------
# Output Schema
# -------------------------------------------------------------------
class DailyEnergyRecord(BaseModel):
    record_date: date
    consumption_kwh: float


class MultiDayEnergyData(BaseModel):
    daily_records: List[DailyEnergyRecord]


# -------------------------------------------------------------------
# Agent Definition
# -------------------------------------------------------------------
consumption_data_agent = Agent(
    name="consumption_data_agent",
    model="gemini-2.5-flash",
    description="Produces daily energy consumption data.",
    instruction="""
    Generate energy consumption data between {baseline_from_date} to {baseline_end_date} for location {city}.
    """,
    output_schema=MultiDayEnergyData,
    output_key="energy_consumption_data",
   #before_model_callback=date_check_before_before_model_call,
)


# -------------------------------------------------------------------
# Session + Runner Setup
# -------------------------------------------------------------------
APP_NAME = "date_checker_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
def main():
    asyncio.run(call_agent_async(
        "Generate energy consumption data between {baseline_from_date} to {baseline_end_date} for location {city}"
    ))


if __name__ == "__main__":
    main()
