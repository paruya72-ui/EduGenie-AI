import os

from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()


# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()


# Local explanation model configuration
LOCAL_EXPLANATION_ENABLED = (
    os.getenv("LOCAL_EXPLANATION_ENABLED", "false").lower() == "true"
)

LOCAL_EXPLANATION_MODEL = os.getenv(
    "LOCAL_EXPLANATION_MODEL",
    "MBZUAI/LaMini-Flan-T5-783M"
).strip()


# Application limits
MAX_INPUT_CHARS = int(
    os.getenv("MAX_INPUT_CHARS", "20000")
)

REQUEST_TIMEOUT_SECONDS = int(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "90")
)