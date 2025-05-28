"""
scheduler.py

Schedules the RevitSlave script to rerun itself every week on Friday night.
This is your automation butler—never miss a beat!
"""

import subprocess
import sys
from pathlib import Path


def schedule_weekly_run(script_path: Path, time: str = "23:00", day: str = "FRI") -> None:
    """
    Schedules this script to run every week on the specified day and time using Windows Task Scheduler.

    Args:
        script_path (Path): The path to the script to schedule.
        time (str): Time in HH:MM (24-hour) format. Default is 23:00.
        day (str): Day of the week (e.g., 'FRI'). Default is 'FRI'.
    """
    task_name = "RevitSlaveWeeklyRun"
    cmd = [
        "schtasks",
        "/Create",
        "/SC", "WEEKLY",
        "/D", day,
        "/TN", task_name,
        "/TR", f'python "{script_path}"',
        "/ST", time,
        "/F"
    ]
    subprocess.run(cmd, check=True) 