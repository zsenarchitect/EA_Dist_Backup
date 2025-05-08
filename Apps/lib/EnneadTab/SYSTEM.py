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



import NOTIFICATION, DATA_FILE, EXE, FOLDER, ENVIRONMENT


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
        NOTIFICATION.messenger("Your computer has been running for {} days and {} hours. Consider restarting your computer for optimal performance.\nNo one work their donkey this hard.".format(days, hours))
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
        (0.6, "MonitorDriveSilent"),
        (0.01, "AccAutoRestarter"),
        (0.5, "RegisterAutoStartup"),
        (0.8, "Rhino8RuiUpdater"),
        (0.5, check_system_uptime),
        (0.3, purge_powershell_folder)
    ]
    
    # Run checks based on probability
    for probability, check in checks:
        if random_value < probability:
            if callable(check):
                check()
            else:
                EXE.try_open_app(check, safe_open=True)
    
    # Update last check time in environment variable
    os.environ[env_var_name] = str(time.time())
    
    return True

# Run system checks when module is imported
run_system_checks()
