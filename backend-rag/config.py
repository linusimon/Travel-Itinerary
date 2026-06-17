import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    # GENAI_BASE_URL="https://genailab.tcs.in"
    # GENAI_API_KEY = os.getenv("GENAI_API_KEY", "YOUR_KEY _HERE")
    # # Model Configuration
    # CHAT_MODEL = "azure_ai/genailab-maas-Deepseek-V3-0324"
    # Flask Configuration
    FLASK_PORT = 5001
    FLASK_HOST = "0.0.0.0"
    DEBUG = True

    GENAI_API_KEY = os.getenv("HF_TOKEN")
    GENAI_BASE_URL = "https://genailab.tcs.in/"
    CHAT_MODEL = "azure/genailab-maas-gpt-4o"