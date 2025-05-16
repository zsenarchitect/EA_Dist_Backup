"""
Constants and configuration settings for EnneadTabAgent

This module centralizes all constants used throughout the application
"""

import os
from pathlib import Path

# Vector store settings
VECTOR_STORE_MAX_AGE_DAYS = 7
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Web scraping settings
BASE_URL = "https://ennead.com"
MAX_PAGES = 500
MAX_DEPTH = 3
URLS_TO_VISIT = [
    BASE_URL,
    BASE_URL + "/work",
    BASE_URL + "/about",
    BASE_URL + "/news",
    BASE_URL + "/careers",
    BASE_URL + "/contact"
]

# OpenAI API settings
MODEL_NAME = "gpt-4"
TEMPERATURE = 0.7
MAX_TOKENS = 1024
SYSTEM_PROMPT = """You are EnneadAssistant, a helpful AI assistant for Ennead Architects. 
You have access to information about Ennead Architects, their projects, philosophy, and services.
Always answer questions based on the provided context when available. 
If you don't know the answer or don't have relevant information in your knowledge base, say so clearly.
Be professional, concise, and helpful. Your responses should reflect Ennead's design philosophy and values.
"""

# UI settings
WINDOW_TITLE = "EnneadAssistant"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400
PRIMARY_COLOR = "#004d7c"  # Ennead blue
SECONDARY_COLOR = "#6d6e71"  # Ennead gray
BACKGROUND_COLOR = "#f5f5f5"  # Light gray background
TEXT_COLOR = "#333333"  # Dark gray text
USER_MESSAGE_COLOR = "#e6f2ff"  # Light blue for user messages
AI_MESSAGE_COLOR = "#ffffff"  # White for AI messages
FONT_FAMILY = "Segoe UI"  # Default font
FONT_SIZE_NORMAL = 11
FONT_SIZE_SMALL = 9
FONT_SIZE_LARGE = 13

# Suggested queries
SUGGESTED_QUERIES = [
    "What are Ennead Architects' most notable projects?",
    "Tell me about Ennead's design philosophy",
    "What services does Ennead Architects offer?",
    "How can I contact Ennead Architects?",
    "What is Ennead's approach to sustainable design?",
    "Who are the partners at Ennead?",
    "What office locations does Ennead have?",
    "What awards has Ennead won?",
    "What are Ennead's current job openings?",
    "Tell me about Ennead's history"
]

# File paths
def get_app_data_dir():
    """Get the application data directory."""
    # Use %APPDATA% on Windows, ~/.config on Linux, ~/Library/Application Support on Mac
    home = Path.home()
    if os.name == 'nt':  # Windows
        return Path(os.environ.get('APPDATA', '')) / "EnneadTabAgent"
    elif os.name == 'posix':  # macOS/Linux
        if os.path.exists(home / "Library" / "Application Support"):  # macOS
            return home / "Library" / "Application Support" / "EnneadTabAgent"
        else:  # Linux
            return home / ".config" / "EnneadTabAgent"
    else:
        return home / ".EnneadTabAgent"

# Create app data directory if it doesn't exist
APP_DATA_DIR = get_app_data_dir()
os.makedirs(APP_DATA_DIR, exist_ok=True)

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = APP_DATA_DIR / "ennead_agent.log"
CHAT_LOG_DIR = APP_DATA_DIR / "chat_logs"
os.makedirs(CHAT_LOG_DIR, exist_ok=True) 