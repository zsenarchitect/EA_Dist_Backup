"""
main.py

Entry point for RevitSlave automation. Loads model data, sets up logging, and runs tasks with debug output.
"""

import sys
from pathlib import Path
import os
import json
import logging
from datetime import datetime

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parents[5]))  # Adjust if needed

from Apps.lib.EnneadTab.scripts.RevitSlave.models import RevitModel
from Apps.lib.EnneadTab.scripts.RevitSlave.task_manager import TaskManager
from Apps.lib.EnneadTab.scripts.RevitSlave.version_control import VersionControl
from Apps.lib.EnneadTab.scripts.RevitSlave.config import Config
from Apps.lib.EnneadTab.scripts.RevitSlave.data_utils import iter_valid_model_dicts
from Apps.lib.EnneadTab.scripts.RevitSlave.scheduler import schedule_weekly_run
from Apps.lib.EnneadTab.scripts.RevitSlave.sample_task import print_title_task

__version__ = "1.0.0"
print ("will use Revit Jornual File to operate revit to do cloud modeul task")
def main():
    """
    Main entry point for RevitSlave automation.
    Loads model data, sets up logging, and runs tasks with debug output.
    """
    config_path = Path(__file__).parent / "config.json"
    config = Config.from_file(config_path)
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO), format='[%(levelname)s] %(message)s')
    logger = logging.getLogger("RevitSlave")
    logger.info("Starting RevitSlave in debug mode!")

    data_file = config.data_file
    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        return
    with open(data_file, 'r') as f:
        data = json.load(f)
    logger.info(f"Loaded model data from {data_file}")

    # Parse valid models
    models = [RevitModel.from_data_dict(name, model_dict) for name, model_dict in data.items() if isinstance(model_dict, dict) and "revit_version" in model_dict]
    logger.info(f"Parsed {len(models)} valid Revit models.")

    # Set up version control and task manager
    version_control = VersionControl(data_file)
    task_manager = TaskManager(version_control, max_workers=config.max_workers)

    # Register and run the sample print_title task
    task_manager.register_task("print_title", print_title_task)
    results = task_manager.execute_tasks_batch("print_title", models)
    logger.info(f"Task results: {results}")

    # Schedule weekly rerun
    schedule_weekly_run(Path(__file__).absolute())
    logger.info("Scheduled weekly rerun on Friday night.")

if __name__ == "__main__":
    main() 