# Configuration for thresholds, email settings, etc. 
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY") 
AGENT_NAME=os.getenv("AGENT_NAME")
AGENT_EMAIL_ADDRESS= os.getenv("AGENT_EMAIL_ADDRESS") 
AGENT_EMAIL_PASSWORD= os.getenv("AGENT_EMAIL_PASSWORD")  
BOSS_NAME=os.getenv("BOSS_NAME")
BOSS_EMAIL_ADDRESS=os.getenv("BOSS_EMAIL_ADDRESS")
DB_PATH = "database/data.db"