from google.genai import types
SHARED_RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier (exponential backoff)
    initial_delay=1, # Initial delay in seconds
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)