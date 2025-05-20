import os
from dotenv import load_dotenv

load_dotenv()

HA_BASE_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")
