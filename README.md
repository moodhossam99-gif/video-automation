# video-automation
Free AI video automation system
import os

API_KEY = os.getenv("API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")

if not API_KEY:
    raise ValueError("API_KEY is missing from environment variables!")

print("Keys loaded successfully. Starting automation...")
