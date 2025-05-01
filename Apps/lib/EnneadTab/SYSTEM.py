#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
EnneadTab System Utilities

Provides system-level utilities and monitoring functions for the EnneadTab ecosystem.
Includes system uptime monitoring, resource checks, and system health notifications.
"""

import time
from EnneadTab import NOTIFICATION, DATA_FILE

def get_system_uptime():
    """Get system uptime in seconds for Windows systems, compatible with both Python 3 and IronPython 2.7.
    
    Returns:
        float: System uptime in seconds. Returns 0 if calculation fails.
    """
    try:
        # Try IronPython 2.7 approach first
        from System.Diagnostics import Process
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
    
    if True or uptime > 7 * 24 * 60 * 60:  # 7 days in seconds
        days = int(uptime / (24 * 60 * 60))
        hours = int((uptime % (24 * 60 * 60)) / (60 * 60))
        NOTIFICATION.messenger("Your computer has been running for {} days and {} hours. Consider restarting your computer for optimal performance.\nNo one work their donkey this hard.".format(days, hours))
    return uptime

check_system_uptime()