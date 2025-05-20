import os
import win32com.client
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Tuple, Set, Generator, Optional
from tqdm import tqdm
import time
from functools import lru_cache
import re
import json
import subprocess
from datetime import datetime
import logging
from collections import defaultdict
import threading
from queue import Queue
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global cache for COM objects
_shell_cache = None
_shell_lock = threading.Lock()

def get_shell():
    """Get or create a cached shell object."""
    global _shell_cache
    if _shell_cache is None:
        with _shell_lock:
            if _shell_cache is None:
                _shell_cache = win32com.client.Dispatch("WScript.Shell")
    return _shell_cache

# Cache for shortcut targets to avoid repeated COM calls
@lru_cache(maxsize=10000)
def get_shortcut_target(shortcut_path: str) -> str:
    """Get the target path of a Windows shortcut file.
    
    Args:
        shortcut_path: Path to the .lnk file
        
    Returns:
        Target path of the shortcut
    """
    try:
        shell = get_shell()
        shortcut = shell.CreateShortCut(shortcut_path)
        return shortcut.Targetpath
    except Exception as e:
        logger.debug("Error getting shortcut target for {}: {}".format(shortcut_path, str(e)))
        return ""

def get_project_folders(drive_path: str = "J:\\") -> Set[str]:
    """Get all immediate project folders in the drive.
    
    Args:
        drive_path: Root path to scan (default: J:\\)
        
    Returns:
        Set of project folder paths
    """
    try:
        return {f.path for f in os.scandir(drive_path) if f.is_dir()}
    except Exception as e:
        logger.error("Error accessing {}: {}".format(drive_path, str(e)))
        return set()

def scan_folder_batch(folder_batch: List[str], project_folders: Set[str], max_depth: int = 3) -> Dict[str, List[Tuple[str, str]]]:
    """Scan a batch of folders for shortcuts pointing to project folders.
    
    Args:
        folder_batch: List of folders to scan
        project_folders: Set of project folder paths to check against
        max_depth: Maximum folder depth to scan (default: 3)
        
    Returns:
        Dictionary mapping folders to their project shortcuts
    """
    results = defaultdict(list)
    project_folders_list = sorted(project_folders)  # Sort for binary search optimization
    
    for folder_path in folder_batch:
        try:
            for root, dirs, files in os.walk(folder_path):
                # Calculate current depth
                current_depth = root[len(folder_path):].count(os.sep)
                if current_depth > max_depth:
                    # Skip deeper directories
                    dirs[:] = []
                    continue
                    
                # Filter for .lnk files first to avoid unnecessary processing
                lnk_files = [f for f in files if f.lower().endswith('.lnk')]
                if not lnk_files:
                    continue
                    
                for file in lnk_files:
                    shortcut_path = os.path.join(root, file)
                    try:
                        target = get_shortcut_target(shortcut_path)
                        if target and any(target.startswith(project) for project in project_folders_list):
                            results[folder_path].append((shortcut_path, target))
                    except Exception as e:
                        logger.debug("Error processing {}: {}".format(shortcut_path, str(e)))
        except Exception as e:
            logger.error("Error scanning {}: {}".format(folder_path, str(e)))
    return dict(results)

def scan_folders_batch(drive_path: str, project_folders: Set[str], batch_size: int = 1000, max_depth: int = 3) -> Generator[Set[str], None, None]:
    """Scan folders in batches to reduce memory usage.
    
    Args:
        drive_path: Root path to scan
        project_folders: Set of project folder paths to exclude
        batch_size: Number of folders to collect before yielding
        max_depth: Maximum folder depth to scan (default: 3)
        
    Yields:
        Sets of folder paths
    """
    current_batch = set()
    project_folders_set = frozenset(project_folders)  # Optimize set operations
    processed_paths = set()  # Track processed paths to avoid duplicates
    
    try:
        for root, dirs, _ in os.walk(drive_path):
            # Calculate current depth
            current_depth = root[len(drive_path):].count(os.sep)
            if current_depth > max_depth:
                # Skip deeper directories
                dirs[:] = []
                continue
                
            # Filter directories before processing
            valid_dirs = [d for d in dirs if os.path.join(root, d) not in project_folders_set]
            
            for dir_name in valid_dirs:
                full_path = os.path.join(root, dir_name)
                if full_path not in processed_paths:  # Only process new paths
                    processed_paths.add(full_path)
                    current_batch.add(full_path)
                    if len(current_batch) >= batch_size:
                        logger.debug("Yielding batch of {} folders".format(len(current_batch)))
                        yield current_batch
                        current_batch = set()
    except Exception as e:
        logger.error("Error during folder scanning: {}".format(str(e)))
        if current_batch:
            yield current_batch
            
    if current_batch:
        logger.debug("Yielding final batch of {} folders".format(len(current_batch)))
        yield current_batch

def save_results_to_json(results: Dict[str, List[Tuple[str, str]]], desktop_path: str) -> str:
    """Save results to a JSON file on desktop.
    
    Args:
        results: Dictionary of results to save
        desktop_path: Path to desktop
        
    Returns:
        Path to the saved JSON file
    """
    json_results = {
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shortcuts": []
    }
    
    # Process results with progress bar
    logger.info("Processing results for JSON...")
    for folder, shortcuts in tqdm(results.items(), desc="Processing results", unit="folder"):
        for shortcut_path, target in shortcuts:
            json_results["shortcuts"].append({
                "folder": folder,
                "shortcut": shortcut_path,
                "target": target
            })
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(desktop_path, "project_shortcuts_{}.json".format(timestamp))
    
    # Save to JSON file with error handling
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        return json_path
    except Exception as e:
        logger.error("Error saving results to JSON: {}".format(str(e)))
        raise

def find_nested_project_shortcuts(drive_path: str = "J:\\", timeout: int = 10, batch_size: int = 50, max_depth: int = 3) -> Dict[str, List[Tuple[str, str]]]:
    """Find shortcuts pointing to project folders using parallel processing.
    
    Args:
        drive_path: Root path to scan (default: J:\\)
        timeout: Maximum time in seconds to scan each folder (default: 10)
        batch_size: Number of folders to process in each batch (default: 50)
        max_depth: Maximum folder depth to scan (default: 3)
        
    Returns:
        Dictionary mapping folders to their project shortcuts
    """
    logger.info("Starting project shortcut scan...")
    start_time = time.time()
    
    # First, get all project folders
    logger.info("Collecting project folders...")
    project_folders = get_project_folders(drive_path)
    logger.info("Found {} project folders".format(len(project_folders)))
    
    # Get all folders to scan (excluding project folders themselves)
    logger.info("Scanning folders (this may take a while for large drives)...")
    results = {}
    total_folders = 0
    processed_batches = 0
    
    # Process folders in batches to reduce memory usage
    with tqdm(desc="Collecting folders", unit="batch") as pbar:
        for folder_batch in scan_folders_batch(drive_path, project_folders, batch_size, max_depth):
            if not folder_batch:  # Skip empty batches
                continue
                
            total_folders += len(folder_batch)
            processed_batches += 1
            logger.info("Processing batch {} with {} folders".format(processed_batches, len(folder_batch)))
            pbar.update(1)
            
            # Process each batch of folders
            with ProcessPoolExecutor() as executor:
                future_to_batch = {
                    executor.submit(scan_folder_batch, list(folder_batch), project_folders, max_depth): i 
                    for i in range(len(folder_batch) // batch_size + 1)
                }
                
                for future in as_completed(future_to_batch):
                    try:
                        batch_results = future.result(timeout=timeout)
                        if batch_results:  # Only update if we found results
                            results.update(batch_results)
                    except TimeoutError:
                        logger.warning("Timeout scanning batch")
                    except Exception as e:
                        logger.error("Error scanning batch: {}".format(str(e)))

    elapsed_time = time.time() - start_time
    logger.info("Scan completed in {:.2f} seconds".format(elapsed_time))
    logger.info("Scanned {} folders in {} batches".format(total_folders, processed_batches))
    return results

def main():
    """Main function to find and display nested project shortcuts."""
    try:
        logger.info("Starting scan for nested project shortcuts in J: drive...")
        results = find_nested_project_shortcuts(max_depth=3)  # Set max depth to 3 levels
        
        if not results:
            logger.info("No project shortcuts found.")
            return

        # Get desktop path
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Save results to JSON
        json_path = save_results_to_json(results, desktop_path)
        logger.info("Results saved to: {}".format(json_path))
        
        # Open the JSON file
        try:
            subprocess.run(['start', json_path], shell=True)
            logger.info("Opening results file...")
        except Exception as e:
            logger.error("Error opening file: {}".format(str(e)))
            logger.info("Please open the file manually: {}".format(json_path))
    except Exception as e:
        logger.error("An error occurred: {}".format(str(e)))
        sys.exit(1)

if __name__ == "__main__":
    main()
