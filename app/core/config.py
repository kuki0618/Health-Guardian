from dotenv import load_dotenv
import os

load_dotenv()

DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")
AMAP_API_KEY = os.getenv("AMAP_API_KEY")
DB_HOST=os.getenv("DB_HOST")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_NAME=os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306)) 
AGENT_ID = os.getenv("AGENT_ID")
