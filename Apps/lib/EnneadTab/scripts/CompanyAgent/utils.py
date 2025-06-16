"""
Utility functions for EnneadTabAgent

This module provides:
- API key management
- File system operations
- Logging setup
- Integration with other EnneadTab modules
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

from . import constants

# Try to import EnneadTab utilities
try:
    # Get the path to DarkSide/exes/source code
    current_dir = os.path.dirname(os.path.abspath(__file__))
    darkside_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))), 
        "DarkSide", 
        "exes", 
        "source code"
    )
    if darkside_path not in sys.path:
        sys.path.insert(0, darkside_path)
    import _Exe_Util
    HAVE_ENNEAD_TOOLS = True
except ImportError:
    HAVE_ENNEAD_TOOLS = False
    print("Warning: EnneadTab utilities not found. Some functionality may be limited.")

# Initialize logger
logger = logging.getLogger("EnneadTabAgent.utils")

def setup_logging():
    """Configure logging for the application."""
    try:
        # Create a formatter
        formatter = logging.Formatter(constants.LOG_FORMAT)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, constants.LOG_LEVEL))
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Create handlers
        file_handler = logging.FileHandler(constants.LOG_FILE)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logger.info("Logging initialized")
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Set up basic logging as fallback
        logging.basicConfig(
            level=getattr(logging, constants.LOG_LEVEL),
            format=constants.LOG_FORMAT,
            handlers=[
                logging.FileHandler(constants.LOG_FILE),
                logging.StreamHandler()
            ]
        )

def get_openai_api_key():
    """Get OpenAI API key from EnneadTab or environment."""
    # First try to get it from EnneadTab
    if HAVE_ENNEAD_TOOLS:
        try:
            api_key = _Exe_Util.get_openai_api_key("EnneadTabAPI")
            if api_key:
                return api_key
        except Exception as e:
            logger.error(f"Error getting API key from EnneadTab: {e}")
    
    # Try environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
        
    # Try looking for a key file
    key_file = constants.APP_DATA_DIR / "api_key.txt"
    if os.path.exists(key_file):
        try:
            with open(key_file, "r") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading API key file: {e}")
            
    logger.warning("No API key found")
    return None
    
def save_api_key(api_key):
    """Save API key to file."""
    try:
        key_file = constants.APP_DATA_DIR / "api_key.txt"
        with open(key_file, "w") as f:
            f.write(api_key)
        return True
    except Exception as e:
        logger.error(f"Error saving API key: {e}")
        return False
        
def get_storage_path(filename):
    """Get path for storing data files."""
    return constants.APP_DATA_DIR / filename
    
def save_chat_log(messages):
    """Save chat conversation to log file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = constants.CHAT_LOG_DIR / f"chat_{timestamp}.json"
        with open(log_file, "w") as f:
            json.dump(messages, f, indent=2)
        return log_file
    except Exception as e:
        logger.error(f"Error saving chat log: {e}")
        return None
        
def load_chat_logs(limit=5):
    """Load recent chat logs."""
    try:
        log_files = sorted(
            constants.CHAT_LOG_DIR.glob("*.json"),
            key=os.path.getmtime,
            reverse=True
        )
        
        logs = []
        for log_file in log_files[:limit]:
            try:
                with open(log_file, "r") as f:
                    logs.append(json.load(f))
            except Exception as e:
                logger.error(f"Error loading chat log {log_file}: {e}")
                
        return logs
    except Exception as e:
        logger.error(f"Error loading chat logs: {e}")
        return []
        
def check_internet_connection():
    """Check if internet connection is available."""
    try:
        # Try to connect to OpenAI's website
        urllib.request.urlopen("https://api.openai.com", timeout=1)
        return True
    except urllib.error.URLError:
        return False
        
def find_username():
    """Get the current username."""
    try:
        if HAVE_ENNEAD_TOOLS:
            try:
                return _Exe_Util.get_current_username()
            except:
                pass
                
        import getpass
        return getpass.getuser()
    except:
        return "User"
        
def format_timestamp(dt=None):
    """Format timestamp for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%I:%M %p")  # 12-hour format with AM/PM
    
def open_url(url):
    """Open a URL in the default browser."""
    import webbrowser
    webbrowser.open(url)
    
def get_vector_store_age():
    """Get age of vector store in days."""
    try:
        vector_store_path = get_storage_path("ennead_knowledge.pkl")
        if not os.path.exists(vector_store_path):
            return None
            
        mtime = datetime.fromtimestamp(os.path.getmtime(vector_store_path))
        days = (datetime.now() - mtime).days
        return days
    except Exception as e:
        logger.error(f"Error getting vector store age: {e}")
        return None 