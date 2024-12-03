"""
Utility functions for logging and progress tracking.
"""

from tqdm import tqdm
from colorama import Fore, Style
from functools import wraps
from datetime import datetime

def log_progress(message, start_time):
    """
    Log progress with a timestamp and elapsed time.

    Args:
        message (str): The progress message to log.
        start_time (datetime): The start time to calculate elapsed time.
    """
    current_time = datetime.now()
    elapsed_time = current_time - start_time
    print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] {message} (Elapsed: {elapsed_time})")

    
def progress_bar_decorator(desc):
    """
    Decorator to add a progress bar to a function.

    Args:
        desc (str): Description for the progress bar.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            a,b,result = func(*args, **kwargs)

            with tqdm(total=len(result), desc=Fore.GREEN + desc + Style.RESET_ALL, 
                      unit="file", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as pbar:
                for _ in result:
                    pbar.update(1)
            end_time = datetime.now()
            elapsed_time = end_time - start_time
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] {desc} completed in {elapsed_time}")
            return a, b, result
        return wrapper
    return decorator



def format_size(size_in_bytes):
    """
    Format the size from bytes to a human-readable format.

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Human-readable size.
    """
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024 or unit == 'TB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024