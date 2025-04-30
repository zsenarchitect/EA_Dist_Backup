#!/usr/bin/env python
# -*- coding: utf-8 -*-

raise Exception("this is no longer used....... moving to MonitorDrive.exe")

"""
Network Drive Performance Monitor

This script monitors the connection status and performance of all drives.
It provides real-time metrics including:
- Connection status
- Read/Write speeds
- Latency
- Overall health status

Usage:
    Run the script to get a comprehensive report of all drives.
    The script will automatically detect and monitor both local and network drives.
    An HTML report will be generated and opened in your default browser.

Author: EnneadTab Team
"""

import os
import time
import psutil
import socket
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, List, Tuple

KNOWN_NETWORK_PATHS = {
    "I:": r"\\ad.ennead.com\dfs",
    "J:": r"\\ea\dfs",
    "L:": r"\\ad.ennead.com\dfs\Library",
    "M:": r"\\ad.ennead.com\dfs\MANAGEMENT",
    "N:": r"\\ad.ennead.com\dfs\NYSH-mgmt",
    "O:": r"\\ad.ennead.com\dfs\OFFICE",
    "P:": r"\\ea\dfs\users",
    "S:": r"\\ad.ennead.com\dfs\PROGRAMS",
    "T:": r"\\ad.ennead.com\dfs",
    "W:": "Peercollabs"
}

class DriveMonitor:
    def __init__(self):
        self.drives = self._get_all_drives()
        self.results = {}

    def _get_all_drives(self) -> List[Dict]:
        """Get list of all available drives with their properties."""
        drives = []
        print("\nScanning for all drives...")
        
        # Method 1: Get all mounted drives using psutil
        for partition in psutil.disk_partitions(all=True):
            drive_info = {
                'path': partition.mountpoint,
                'type': partition.fstype,
                'is_network': 'remote' in partition.opts.lower(),
                'name': KNOWN_NETWORK_PATHS.get(partition.mountpoint, partition.mountpoint)
            }
            print(f"Found drive: {drive_info['path']} (Type: {drive_info['type']}, Network: {drive_info['is_network']})")
            drives.append(drive_info)
        
        # Method 2: Check net use command for network drives
        try:
            result = subprocess.check_output("net use", shell=True).decode('utf-8', errors='ignore')
            for line in result.split('\n'):
                if '\\\\' in line and ':' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        drive_letter = parts[1] if parts[1].endswith(':') else parts[0]
                        network_path = parts[0] if parts[0].startswith('\\\\') else parts[2]
                        if not any(d['path'].startswith(drive_letter) for d in drives):
                            drive_info = {
                                'path': drive_letter,
                                'type': 'NETWORK',
                                'is_network': True,
                                'name': network_path
                            }
                            print(f"Found network drive: {drive_info['path']} -> {drive_info['name']}")
                            drives.append(drive_info)
        except Exception as e:
            print(f"Error checking net use: {e}")
        
        # Method 3: Check all possible drive letters
        all_letters = [f"{chr(i)}:" for i in range(65, 91)]  # A: to Z:
        for letter in all_letters:
            if os.path.exists(letter) and not any(d['path'].startswith(letter) for d in drives):
                try:
                    drive_type = 'NETWORK' if letter in KNOWN_NETWORK_PATHS else 'LOCAL'
                    drive_info = {
                        'path': letter,
                        'type': drive_type,
                        'is_network': drive_type == 'NETWORK',
                        'name': KNOWN_NETWORK_PATHS.get(letter, letter)
                    }
                    print(f"Found additional drive: {drive_info['path']} ({drive_info['type']})")
                    drives.append(drive_info)
                except:
                    continue
        
        print(f"\nTotal drives found: {len(drives)}")
        return drives

    def _test_connection(self, drive: Dict) -> Tuple[bool, float]:
        """Test connection to drive and measure latency."""
        try:
            print(f"\nTesting connection to {drive['path']} ({drive['name']})...")
            start_time = time.time()
            # Try to list contents of root directory
            os.listdir(drive['path'])
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            print(f"Connection successful. Latency: {latency:.2f} ms")
            return True, latency
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False, float('inf')

    def _test_speed(self, drive: Dict) -> Tuple[float, float]:
        """Test read and write speeds of drive."""
        # Try different locations for speed test
        test_locations = [
            os.path.join(os.getenv('TEMP'), f'drive_speed_test_{os.path.splitdrive(drive["path"])[0].rstrip(":")}'),  # Local temp folder
            os.path.join(drive['path'], 'Temp'),  # Temp folder
            os.path.join(drive['path'], '.EnneadTab', 'temp'),  # EnneadTab temp folder
            os.path.join(drive['path'], 'Users', os.getenv('USERNAME')),  # User folder
        ]
        
        test_size = 1024 * 1024  # 1MB test file
        print(f"\nTesting speeds for {drive['path']}...")
        
        for test_location in test_locations:
            test_file = os.path.join(test_location, "speed_test.tmp")
            print(f"Attempting speed test in: {test_location}")
            
            try:
                # Create directory if it doesn't exist (skip if creation fails)
                try:
                    os.makedirs(test_location, exist_ok=True)
                except Exception as e:
                    print(f"Cannot create test directory {test_location}: {str(e)}")
                    continue
                
                # Write test
                start_time = time.time()
                with open(test_file, 'wb') as f:
                    f.write(os.urandom(test_size))
                write_time = time.time() - start_time
                write_speed = (test_size / write_time) / (1024 * 1024)  # MB/s
                print(f"Write speed: {write_speed:.2f} MB/s")
                
                # Read test
                start_time = time.time()
                with open(test_file, 'rb') as f:
                    f.read()
                read_time = time.time() - start_time
                read_speed = (test_size / read_time) / (1024 * 1024)  # MB/s
                print(f"Read speed: {read_speed:.2f} MB/s")
                
                # Cleanup
                try:
                    os.remove(test_file)
                except Exception as e:
                    print(f"Warning: Could not remove test file {test_file}: {str(e)}")
                
                return read_speed, write_speed
                
            except Exception as e:
                print(f"Speed test failed in {test_location}: {str(e)}")
                # Cleanup on failure
                if os.path.exists(test_file):
                    try:
                        os.remove(test_file)
                    except:
                        pass
        
        print("All speed test locations failed")
        return 0.0, 0.0

    def _get_drive_info(self, drive: Dict) -> Dict:
        """Get detailed information about a drive."""
        try:
            print(f"Getting storage info for {drive['path']}...")
            usage = psutil.disk_usage(drive['path'])
            info = {
                'total': usage.total / (1024**3),  # Convert to GB
                'used': usage.used / (1024**3),
                'free': usage.free / (1024**3),
                'percent': usage.percent
            }
            print(f"Storage info: {info}")
            return info
        except Exception as e:
            print(f"Failed to get storage info: {str(e)}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    def monitor(self) -> Dict:
        """Monitor all drives and return results."""
        if not self.drives:
            print("\nNo drives found.")
            return {}
            
        for drive in self.drives:
            print(f"\nProcessing drive: {drive['path']} ({drive['name']})")
            drive_info = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': drive['name'],
                'type': drive['type'],
                'is_network': drive['is_network'],
                'status': 'Unknown',
                'latency': 0,
                'read_speed': 0,
                'write_speed': 0,
                'space_info': {}
            }
            
            # Test connection
            is_connected, latency = self._test_connection(drive)
            drive_info['latency'] = latency
            
            if is_connected:
                # Test speeds
                read_speed, write_speed = self._test_speed(drive)
                drive_info['read_speed'] = read_speed
                drive_info['write_speed'] = write_speed
                
                # Get drive info
                drive_info['space_info'] = self._get_drive_info(drive)
                
                # Determine status
                if drive['is_network']:
                    if latency < 100 and read_speed > 1 and write_speed > 1:
                        drive_info['status'] = 'Good'
                    elif latency < 500 and read_speed > 0.5 and write_speed > 0.5:
                        drive_info['status'] = 'Fair'
                    else:
                        drive_info['status'] = 'Poor'
                else:
                    if read_speed > 50 and write_speed > 50:
                        drive_info['status'] = 'Good'
                    elif read_speed > 10 and write_speed > 10:
                        drive_info['status'] = 'Fair'
                    else:
                        drive_info['status'] = 'Poor'
            else:
                drive_info['status'] = 'Disconnected'
            
            self.results[drive['path']] = drive_info
        
        return self.results

    def print_report(self):
        """Print a formatted report of the monitoring results."""
        if not self.results:
            print("\nNo drives were monitored.")
            return
            
        print("\nDrive Performance Report")
        print("=" * 50)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # First print network drives
        print("\nNetwork Drives:")
        print("-" * 50)
        for path, info in self.results.items():
            if info['is_network']:
                self._print_drive_info(path, info)
        
        # Then print local drives
        print("\nLocal Drives:")
        print("-" * 50)
        for path, info in self.results.items():
            if not info['is_network']:
                self._print_drive_info(path, info)

    def _print_drive_info(self, path: str, info: Dict):
        """Helper method to print drive information."""
        print(f"\nDrive: {path}")
        print(f"Name: {info['name']}")
        print(f"Type: {info['type']}")
        print(f"Status: {info['status']}")
        print(f"Latency: {info['latency']:.2f} ms")
        print(f"Read Speed: {info['read_speed']:.2f} MB/s")
        print(f"Write Speed: {info['write_speed']:.2f} MB/s")
        
        if info['space_info']:
            print("\nStorage Information:")
            print(f"Total: {info['space_info']['total']:.2f} GB")
            print(f"Used: {info['space_info']['used']:.2f} GB")
            print(f"Free: {info['space_info']['free']:.2f} GB")
            print(f"Usage: {info['space_info']['percent']}%")
        
        print("-" * 50)

    def generate_html_report(self):
        """Generate an HTML report with the monitoring results."""
        if not self.results:
            return "<h1>No drives were monitored.</h1>"

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Drive Performance Report for Ennead Architects</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .drive-card {{ background-color: white; border-radius: 5px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .status-good {{ color: #27ae60; font-weight: bold; }}
        .status-fair {{ color: #f39c12; font-weight: bold; }}
        .status-poor {{ color: #c0392b; font-weight: bold; }}
        .status-disconnected {{ color: #7f8c8d; font-weight: bold; }}
        .metric {{ margin: 10px 0; }}
        .storage-bar {{ background-color: #ecf0f1; border-radius: 5px; height: 20px; margin: 10px 0; position: relative; }}
        .storage-used {{ background-color: #3498db; height: 100%; border-radius: 5px; transition: width 0.5s ease-in-out; }}
        .storage-text {{ position: absolute; width: 100%; text-align: center; color: black; line-height: 20px; font-size: 12px; }}
        .warning {{ background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Drive Performance Report for Ennead Architects</h1>
        <p>Generated on: {timestamp}</p>
    </div>
"""

        # Network Drives Section
        html += '<div class="section"><h2>Network Drives</h2>'
        for path, info in self.results.items():
            if info['is_network']:
                html += self._generate_drive_card(path, info)
        html += '</div>'

        # Local Drives Section
        html += '<div class="section"><h2>Local Drives</h2>'
        for path, info in self.results.items():
            if not info['is_network']:
                html += self._generate_drive_card(path, info)
        html += '</div>'

        html += """
</body>
</html>
"""
        return html

    def _generate_drive_card(self, path: str, info: Dict) -> str:
        """Generate HTML for a single drive card."""
        status_class = {
            'Good': 'status-good',
            'Fair': 'status-fair',
            'Poor': 'status-poor',
            'Disconnected': 'status-disconnected'
        }.get(info['status'], '')

        warnings = []
        if info['status'] != 'Disconnected':
            if info['space_info'].get('percent', 0) > 85:
                warnings.append(f"Storage usage is critically high ({info['space_info']['percent']}%)")
            if info['latency'] > 500:
                warnings.append(f"High latency detected ({info['latency']:.1f} ms)")
            if info['is_network'] and info['read_speed'] < 0.5:
                warnings.append("Slow read speed")
            if info['is_network'] and info['write_speed'] < 0.5:
                warnings.append("Slow write speed")

        html = f"""
        <div class="drive-card">
            <h3>{path} ({info['name']})</h3>
            <div class="metric">Type: {info['type']}</div>
            <div class="metric">Status: <span class="{status_class}">{info['status']}</span></div>
            <div class="metric">Latency: {info['latency']:.2f} ms</div>
            <div class="metric">Read Speed: {info['read_speed']:.2f} MB/s</div>
            <div class="metric">Write Speed: {info['write_speed']:.2f} MB/s</div>
        """

        if info['space_info']:
            used_percent = info['space_info']['percent']
            html += f"""
            <div class="metric">
                <strong>Storage Information:</strong>
                <div class="storage-bar">
                    <div class="storage-used" style="width: {used_percent}%"></div>
                    <div class="storage-text">
                        {used_percent}% used ({info['space_info']['used']:.2f} GB of {info['space_info']['total']:.2f} GB)
                    </div>
                </div>
                <div>Free Space: {info['space_info']['free']:.2f} GB</div>
            </div>
            """

        if warnings:
            html += '<div class="warning">'
            html += '<strong>Warnings:</strong><br>'
            html += '<br>'.join(warnings)
            html += '</div>'

        html += '</div>'
        return html

    def save_html_report(self):
        """Save the HTML report to the desktop and open in browser."""
        html_content = self.generate_html_report()
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        report_path = os.path.join(desktop_path, 'drive_report.html')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nReport saved to: {report_path}")
        webbrowser.open('file://' + os.path.realpath(report_path))

def main():
    monitor = DriveMonitor()
    monitor.monitor()
    monitor.print_report()  # Keep console output for debugging
    monitor.save_html_report()  # Generate and open HTML report

if __name__ == "__main__":
    main()
