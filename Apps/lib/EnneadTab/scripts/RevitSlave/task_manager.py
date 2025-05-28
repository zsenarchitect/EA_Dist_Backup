"""
Task manager module for RevitSlave.

This module handles the execution and scheduling of Revit automation tasks.
"""

from typing import Dict, List, Optional, Callable
from pathlib import Path
import json
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

from .models import RevitModel, RevitProject
from .version_control import VersionControl


class TaskManager:
    """Manages and executes Revit automation tasks."""
    
    def __init__(self, version_control: VersionControl, max_workers: int = 4):
        """Initialize task manager with version control and worker count."""
        self.version_control = version_control
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Callable] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_task(self, task_id: str, task_func: Callable) -> None:
        """Register a new task function."""
        self._tasks[task_id] = task_func
    
    def execute_task(self, task_id: str, model: RevitModel, **kwargs) -> bool:
        """Execute a task on a specific model."""
        task_func = self._tasks.get(task_id)
        if not task_func:
            self._logger.error(f"Task {task_id} not found")
            return False
            
        try:
            result = task_func(model, **kwargs)
            if result:
                self.version_control.update_model(model)
            return bool(result)
        except Exception as e:
            self._logger.error(f"Error executing task {task_id}: {str(e)}")
            return False
    
    def execute_tasks_batch(self, task_id: str, models: List[RevitModel], **kwargs) -> Dict[str, bool]:
        """Execute a task on multiple models in parallel. Logs errors and waits for all threads to finish."""
        results = {}
        futures = {
            model.model_guid: self._executor.submit(self.execute_task, task_id, model, **kwargs)
            for model in models
        }
        for guid, future in futures.items():
            try:
                result = future.result()
                results[guid] = result
                if not result:
                    logging.error(f"Task '{task_id}' failed for model GUID: {guid}")
            except Exception as e:
                results[guid] = False
                logging.error(f"Exception in task '{task_id}' for model GUID: {guid}: {e}")
        return results
    
    def shutdown(self) -> None:
        """Shutdown the task manager and its thread pool."""
        self._executor.shutdown(wait=True) 