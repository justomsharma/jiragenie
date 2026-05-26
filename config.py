import os
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_PROJECT = os.getenv("DEFAULT_PROJECT")

if not JIRA_BASE_URL:
    raise ValueError("JIRA_BASE_URL not set in .env")

if not JIRA_EMAIL:
    raise ValueError("JIRA_EMAIL not set in .env")

if not JIRA_API_TOKEN:
    raise ValueError("JIRA_API_TOKEN not set in .env")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in .env")