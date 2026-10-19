
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

APP = {
    "name": "SmartSnow",
    "debug": os.getenv("APP_DEBUG", "false").lower() == "true",
    "elevation": {
        "api_key": os.getenv("OPENTOPOGRAPHY_API_KEY"),
        "dataset": "COP30",
        "buffer_meters": 200,
    },
}
