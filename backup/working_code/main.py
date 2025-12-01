import asyncio
import json
import logging
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.genai import types
import os

# NOTE: Ensure 'root_agent' is your Input Agent or Sequential Agent defined elsewhere.
from coordinator_agent.agent import root_agent 
from dotenv import load_dotenv

load_dotenv()  # Loads .env from current directory

api_key = os.getenv("GOOGLE_API_KEY")  # or the variable name you used

# --- Configuration ---
APP_NAME = "multiple_regression_prediction_app"
USER_ID = "multiple_workflow_user"
SESSION_ID = "multiple_workflow_session" 
# Use a specific session ID for reuse, or set to None/unique for fresh sessions.

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_session(
    runner_instance: Runner, user_queries: list[str] | str, session_id: str = "default"
):
    """Helper function to run queries in a session and display responses."""
    print(f"\n### Session: {session_id}")

    # Create or retrieve session
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Stream agent response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Model: > {text}")


print("✅ Helper functions defined.")
async def main(name: str, city: str, baseline_from_date: str, baseline_to_date: str):
    global session_service
    global logger
    session_service = InMemorySessionService()

    # Initialize the runner with logging plugin
    runner = Runner(
        agent=root_agent,
        plugins=[LoggingPlugin()],
        session_service=session_service,
        app_name=APP_NAME,
    )

    # Prepare user input query
    user_input = (
        f"My name is {name}. I live in {city}. "
        f"My baseline start date is {baseline_from_date} and "
        f"my baseline end date is {baseline_to_date}."
    )

    # Run the session with the user input
    await run_session(
        runner_instance=runner,
        user_queries=user_input,
        session_id=SESSION_ID,
    )
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run multiple regression prediction app.")
    parser.add_argument("--name", type=str, required=True, help="User's name")
    parser.add_argument("--city", type=str, required=True, help="User's city")
    parser.add_argument(
        "--baseline_from_date",
        type=str,
        required=True,
        help="Baseline start date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--baseline_to_date",
        type=str,
        required=True,
        help="Baseline end date in YYYY-MM-DD format",
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            name=args.name,
            city=args.city,
            baseline_from_date=args.baseline_from_date,
            baseline_to_date=args.baseline_to_date,
        )
    )