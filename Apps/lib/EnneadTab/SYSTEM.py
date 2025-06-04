#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EnneadTab System Utilities

Provides system-level utilities and monitoring functions for the EnneadTab ecosystem.
Includes system uptime monitoring, resource checks, and system health notifications.
Compatible with both IronPython 2.7 and CPython 3.x environments.
"""
import os
import re
import shutil
import datetime
import time
import random
import json


import NOTIFICATION, DATA_FILE,USER,  EXE, FOLDER, ENVIRONMENT, ERROR_HANDLE


def parse_timestamp(timestamp_str):
    """Parse timestamp string that can be in two different formats.
    
    Args:
        timestamp_str (str): Timestamp in either 'YYYY-MM-DD HH:MM:SS' or 'YYYYMMDD HHMMSS' format
        
    Returns:
        datetime.datetime: Parsed datetime object
        
    Raises:
        ValueError: If timestamp cannot be parsed in either format
    """
    # Try the newer format first (YYYYMMDD HHMMSS)
    try:
        return datetime.datetime.strptime(timestamp_str, "%Y%m%d %H%M%S")
    except ValueError:
        pass
    
    # Try the older format (YYYY-MM-DD HH:MM:SS)
    try:
        return datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # If neither format works, raise an error
    raise ValueError("Cannot parse timestamp: {}".format(timestamp_str))

def alert_missing_schedule_update():
    if not USER.IS_DEVELOPER:
        return

    # Construct file path that works for both IronPython and CPython
    history_filename = "publish_history_SZHANG.json"
    history = os.path.join(ENVIRONMENT.ROOT, "DarkSide", history_filename)
    
    if not os.path.exists(history):
        return
    
    try:
        with open(history, "r") as f:
            data = json.load(f)
    except Exception as e:
        ERROR_HANDLE.print_note("Error reading publish history: {}".format(e))
        return
    
    # Get runs data and check if it exists
    runs = data.get("runs", [])
    if not runs:
        NOTIFICATION.duck_pop("No publish history found! Time to get back to work!")
        return
    
    # Sort records by timestamp (most recent first)
    try:
        sorted_runs = sorted(runs, key=lambda x: parse_timestamp(x["timestamp"]), reverse=True)
    except Exception as e:
        ERROR_HANDLE.print_note("Error sorting publish history: {}".format(e))
        return
    
    # Get most recent record
    most_recent = sorted_runs[0]
    most_recent_timestamp = most_recent["timestamp"]
    most_recent_success = most_recent.get("success", False)
    
    # Parse timestamp and calculate time difference
    try:
        timestamp_dt = parse_timestamp(most_recent_timestamp)
        current_time = datetime.datetime.now()
        time_diff = current_time - timestamp_dt
        
        # Check if more than 1 day old
        is_old = time_diff.total_seconds() > 24 * 60 * 60  # 1 day in seconds
        
        # Alert if most recent is more than 1 day old OR if it failed
        if is_old or not most_recent_success:
            if is_old and not most_recent_success:
                message = "Yikes! Last publish was {} ago AND it failed! Time to fix things up!".format(
                    format_time_diff(time_diff)
                )
            elif is_old:
                message = "Hey there! Last publish was {} ago. Maybe time for an update?".format(
                    format_time_diff(time_diff)
                )
            else:
                message = "Oops! Last publish failed at {}. Better check what went wrong!".format(
                    most_recent_timestamp
                )
            
            print("DEBUG: Would show duck pop message: {}".format(message))
            NOTIFICATION.duck_pop(message)
        else:
            print("DEBUG: All good! Most recent publish at {} was successful and recent.".format(most_recent_timestamp))
            
    except Exception as e:
        ERROR_HANDLE.print_note("Error processing timestamp: {}".format(e))
        return

def format_time_diff(time_diff):
    """Helper function to format time difference in human readable format."""
    days = int(time_diff.total_seconds() // (24 * 60 * 60))
    hours = int((time_diff.total_seconds() % (24 * 60 * 60)) // (60 * 60))
    
    if days > 0:
        if hours > 0:
            return "{} days and {} hours".format(days, hours)
        else:
            return "{} days".format(days)
    else:
        return "{} hours".format(hours)

def get_system_uptime():
    """Get system uptime in seconds for Windows systems, compatible with both Python 3 and IronPython 2.7.
    
    Returns:
        float: System uptime in seconds. Returns 0 if calculation fails.
    """
    try:
        # Try IronPython 2.7 approach first
        from System.Diagnostics import Process # type: ignore
        uptime = time.time() - Process.GetCurrentProcess().StartTime.ToUniversalTime().Ticks / 10000000.0
        if uptime < 0:
            raise ValueError("Negative uptime detected")
        return uptime
    except (ImportError, ValueError):
        try:
            # Try Python 3 approach with ctypes
            import ctypes
            lib = ctypes.windll.kernel32
            tick_count = lib.GetTickCount64()
            return tick_count / 1000.0  # Convert milliseconds to seconds
        except:
            return 0

def check_system_uptime():
    """Check system uptime and send notification if it exceeds 7 days.
    
    Monitors the system's uptime and sends a notification if the system has been
    running for more than 7 days. This helps prevent system performance degradation
    due to extended uptime. Checks are limited to once per hour to avoid spam.
    
    Returns:
        float: System uptime in seconds
    """
    # Get last check time from data file
    last_check_data = DATA_FILE.get_data("system_uptime_check") or {}
    last_check_time = last_check_data.get("last_check_time", 0)
    
    # Only proceed if more than 1 hour has passed since last check
    if time.time() - last_check_time < 3600:  # 3600 seconds = 1 hour
        return last_check_data.get("last_uptime", 0)
    
    uptime = get_system_uptime()
    
    # Update last check time and uptime
    DATA_FILE.set_data({
        "last_check_time": time.time(),
        "last_uptime": uptime
    }, "system_uptime_check")
    
    if uptime > 7 * 24 * 60 * 60:  # 7 days in seconds
        days = int(uptime / (24 * 60 * 60))
        hours = int((uptime % (24 * 60 * 60)) / (60 * 60))
        NOTIFICATION.messenger("Your computer has been running for {} days and {} hours. Consider restarting your computer for optimal performance.\nNo one even work their donkey this hard.".format(days, hours))
    return uptime

def purge_powershell_folder():
    """Clean up PowerShell transcript folders that match YYYYMMDD pattern.
    
    This function:
    1. Scans Documents folder for YYYYMMDD pattern folders
    2. Checks for PowerShell_transcript files inside
    3. Deletes matching folders
    4. Runs once per day using timestamp check
    """
    # Get the documents folder path
    docs_folder = ENVIRONMENT.ONE_DRIVE_DOCUMENTS_FOLDER
    if not os.path.exists(docs_folder):
        return
    
    # Check if we already ran today
    timestamp_file = FOLDER.get_local_dump_folder_file("last_ps_cleanup.txt")
    
    try:
        with open(timestamp_file, 'r') as f:
            last_run = f.read().strip()
            if last_run == datetime.datetime.now().strftime("%Y%m%d"):
                return
    except:
        pass
        
    # Pattern for YYYYMMDD folders
    date_pattern = re.compile(r"^\d{8}$")
    
    folders_to_delete = []
    
    # Scan for matching folders
    for folder_name in os.listdir(docs_folder):
        folder_path = os.path.join(docs_folder, folder_name)
        
        # Check if it's a directory and matches date pattern
        if os.path.isdir(folder_path) and date_pattern.match(folder_name):
            # Check if contains PowerShell transcripts
            has_ps_transcript = False
            for file in os.listdir(folder_path):
                if "PowerShell_transcript" in file:
                    has_ps_transcript = True
                    break
            if len(os.listdir(folder_path)) == 0:
                folders_to_delete.append(folder_path)
                    
            if has_ps_transcript:
                folders_to_delete.append(folder_path)
    
    # Actual deletion
    deleted_count = 0
    for folder in folders_to_delete:
        try:
            # Try to delete entire folder tree first
            shutil.rmtree(folder)
            deleted_count += 1
        except Exception as e:
            # If folder deletion fails, try deleting individual files
            try:
                files = os.listdir(folder)
                for file in files:
                    file_path = os.path.join(folder, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception:
                        continue
                # Try deleting empty folder again
                os.rmdir(folder)
                deleted_count += 1
            except Exception:
                continue
        
    # Update timestamp file
    with open(timestamp_file, 'w') as f:
        f.write(datetime.datetime.now().strftime("%Y%m%d"))
    
    return folders_to_delete


def spec_report():
    """Run the PC fleet summary report."""
    try:
        import sys
        sys.path.append(ENVIRONMENT.SCRIPT_FOLDER)
        import display_pc_spec # type: ignore
        display_pc_spec.main()
    except Exception as e:
        ERROR_HANDLE.print_note("Error running PC fleet summary report: {}".format(e))
        pass


def check_spec():

    file = os.path.join(ENVIRONMENT.SHARED_DUMP_FOLDER,"_internal reports",  "machine_data.json")
    if not os.path.exists(file):
        return
    copy = FOLDER.copy_file_to_local_dump_folder(file, "machine_data.json")
    data = DATA_FILE.get_data("machine_data")
    if data is None:
        return
    if ENVIRONMENT.get_computer_name() in data:
        chance = 0.05
    else:
        chance = 0.4

    if random.random() < chance:
        EXE.try_open_app("ComputerSpec", safe_open=True)
    pass

def run_system_checks():
    """Run system checks with configurable probabilities.
    
    This function runs various system checks and maintenance tasks based on
    random probability values. Each check has its own probability threshold.
    Checks are limited to once per hour to prevent excessive system load using
    environment variables for lightweight tracking between sessions.
    
    Returns:
        bool: True if checks were performed, False if skipped due to frequency limit
    """
    # Check if we already ran recently using environment variable
    env_var_name = "LAST_SYSTEM_CHECK"
    
    try:
        last_check_time_str = os.environ.get(env_var_name, "0")
        last_check_time = float(last_check_time_str)
    except (ValueError, TypeError):
        last_check_time = 0
    
    # Only proceed if more than 1 hour has passed since last check
    if time.time() - last_check_time < 1800:  # 1800 seconds = 30 minutes
        return False
    
    # Generate a single random number for all probability checks
    random_value = random.random()
    
    # Define check probabilities
    checks = [
        (0.2, "MonitorDriveSilent"),
        (0.01, "AccAutoRestarter"),
        (0.5, "RegisterAutoStartup"),
        (0.3, "Rhino8RuiUpdater"),
        (0.5, check_system_uptime),
        (0.3, purge_powershell_folder),
        (0.2, check_spec),
        (0.1, spec_report)
    ]
    
    # Run checks based on probability
    for probability, check in checks:
        if random_value < probability:
            if callable(check):
                check()
            else:
                EXE.try_open_app(check, safe_open=True)

    # this is only for developer and it is handled inside the function
    alert_missing_schedule_update()
    
    # Update last check time in environment variable
    os.environ[env_var_name] = str(time.time())
    
    return True

# Run system checks when module is imported
run_system_checks()
