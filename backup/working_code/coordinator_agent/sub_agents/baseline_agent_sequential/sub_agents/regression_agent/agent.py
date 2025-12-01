from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.google_llm import Gemini
from google.adk.code_executors import BuiltInCodeExecutor
from config.settings import SHARED_RETRY_CONFIG
from typing import Dict, Any, List
from datetime import date, datetime, timedelta
from dateutil.parser import parse, ParserError
from pydantic import BaseModel, Field
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_percentage_error
import traceback

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
logging.info("Instantiated regression_agent")

# -------------------------------------------------------------------
# Output Schema
# -------------------------------------------------------------------
class RegressionRecord(BaseModel):
    record_date: str
    regression_equation: str
    nmbe:float
    mape:float  
    r2:float
    
def run_regression_generic(X: dict, Y: dict):
    """
    Generic Regression tool. 
    Given data of indepedant and depdenat variables, it gives regression equation with its accuracy metrics

    Parameters:
        X (dict): independent variables (e.g., temperature, humidity, dewpoint...)
        Y (dict): dependent variable (energy consumption)

    Returns:
        dict containing:
            status: "success" or "error"
            regression_equation: str
            r2: float
            nmbe: float
            mape: float
    """

    try:
        #print("\n[REGRESSION AGENT] Starting regression...")
        log.info("\n[REGRESSION AGENT] Starting regression...") 

        # Convert dictionary objects to numpy arrays
        X_values = np.array(list(X.values())).T  # shape (n_samples, n_features)
        Y_values = np.array(list(Y.values()))
        feature_names = list(X.keys())
        target_name = list(Y.keys())[0] if len(Y.keys()) == 1 else "target"
        record_date = datetime.now().date()

        #print(f"[INFO] Independent Variables: {feature_names}")
        log.info(f"[INFO] Independent Variables: {feature_names}")
        #print(f"[INFO] Dependent Variable: {target_name}")
        # print("\n[INFO] X Values:")
        # print(X_values)
        # print("\n[INFO] Y Values:")
        # print(Y_values)

        # Train regression model
        model = LinearRegression()
        model.fit(X_values, Y_values)

        predictions = model.predict(X_values)

        # Calculate metrics
        r2 = r2_score(Y_values, predictions)
        mape = mean_absolute_percentage_error(Y_values, predictions)

        # NMBE = Mean((Actual - Predicted)) / Mean(Actual)
        nmbe = np.mean(Y_values - predictions) / np.mean(Y_values)

        # Generate regression equation dynamically
        coef_eq_parts = []
        for coef, name in zip(model.coef_, feature_names):
            coef_eq_parts.append(f"({coef:.4f} * {name})")

        equation = " + ".join(coef_eq_parts)
        equation = f"{target_name} = {model.intercept_:.4f} + " + equation

        #print("\n[REGRESSION EQUATION]")
        log.info(f"REGRESSION EQUATION- {equation}")
        log.info(f"R² Score: {r2}")
        log.info(f"NMBE: {nmbe}")
        log.info(f"MAPE: {mape}")

        log.info(equation)
        # print(equation)
        # print("\n[METRICS]")
        # print(f"R² Score: {r2}")
        # print(f"NMBE: {nmbe}")
        # print(f"MAPE: {mape}")
        return {
            "status": "success",
            "regression_equation": equation,
            "r2": r2,
            "nmbe": nmbe,
            "mape": mape,
            "record_date":record_date
        }
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"\n[ERROR] An error occurred during regression: {error_msg}")
        print(traceback_str)
        return {
            "status": "error",
            "message": error_msg
        }   
regression_agent = Agent(
    name="regression_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model= Gemini (model="gemini-2.5-flash", retry_options=SHARED_RETRY_CONFIG),
    # description="Regression agent",
    # instruction="""
    # Perform the regression analysis.
    # Crucially: Respond ONLY with a valid JSON object that strictly adheres to the provided output_schema.
    # Do not include any introductory or explanatory text.
    # """,
    description="Agent that calculates the Multiple Linear Regression equation parameters.",
    instruction=f"""
    You are an expert in **Multiple Linear Regression**. Your primary task is to read, combine, and analyze data 
    from the preceding 'Consumption_Agent' and 'Weather_Agent'.
    
    1.  **Read History:** Use the BuiltInCodeExecutor to access the entire conversation history. Identify the last JSON output 
        from the 'Consumption_Agent' and the 'Weather_Agent'.
    2.  **Combine Data:** Your Python code must load the JSON outputs, clean/normalize the column names and dates (e.g., merge on date), 
        and combine them into a single pandas DataFrame.
    3.  **Perform Regression:** Fit the model: **Consumption (C) ~ Temperature (T) + Humidity (H) + Dewpoint (D)** on the combined DataFrame.
    4.  **Output Parameters:** The final text response MUST clearly present the calculated intercept and coefficients for T, H, and D.
    
    CRUCIALLY: Append the final calculated parameters to your response using these machine-readable tags:
    [INTERCEPT_START] [INTERCEPT_END]
    [TEMP_COEF_START] [TEMP_COEF_END]
    [HUMIDITY_COEF_START] [HUMIDITY_COEF_END]
    [DEWPOINT_COEF_START] [DEWPOINT_COEF_END]
    """,
    code_executor=BuiltInCodeExecutor(),
    # output_schema and output_key should still be omitted if you use the BuiltInCodeExecutor
)