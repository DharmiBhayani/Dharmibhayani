import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AI Project Manager Agent"
DATABASE_PATH = "data/project.db"

TEMPERATURE = 0.0

# PDF-RAG answer models are configured in models/model_manager.py