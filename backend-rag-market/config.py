import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    FLASK_PORT = 5003
    FLASK_HOST = "0.0.0.0"
    DEBUG = True

    # TCS GenAI Lab Configuration
    GENAI_API_KEY = os.getenv("HF_TOKEN")
    GENAI_BASE_URL = "https://genailab.tcs.in/"
    CHAT_MODEL = "azure/genailab-maas-gpt-4o"
    EMBEDDING_MODEL = "azure/genailab-maas-text-embedding-3-large"

    # Finnhub API Key
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
