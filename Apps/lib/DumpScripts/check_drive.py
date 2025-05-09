"""
Storage History Tracker

Identifies and visualizes storage usage patterns on network drives.
Generates interactive HTML plots showing folder size trends over time,
helping to identify large or rapidly growing project folders.

Key Features:
- Scans specified network drives (I: and J:) to collect folder size data
- Tracks size history over time with persistent data storage
- Generates interactive visualizations with filterable project folders
- Provides trend analysis to identify rapidly growing folders

Dependencies:
- os, pathlib: File system operations
- pandas: Data handling and analysis
- plotly: Interactive visualizations
- datetime: Time-based operations
- json: Data storage
- logging: Error tracking
- tqdm: Progress bar
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import time
import subprocess
import webbrowser
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("drive_history_tracker.log")
    ]
)

# Check for required packages and install if needed
def check_dependencies():
    """
    Check for required dependencies and install them if missing.
    """
    required_packages = ['pandas', 'plotly', 'tqdm']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logging.info(f"Package {package} is already installed.")
        except ImportError:
            missing_packages.append(package)
            logging.warning(f"Package {package} is not installed.")
    
    if missing_packages:
        logging.info(f"Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            logging.info("All required packages installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install packages: {e}")
            print(f"Please install the following packages manually: {', '.join(missing_packages)}")
            print("You can use: pip install " + ' '.join(missing_packages))
            sys.exit(1)

# Now import the dependencies that might have been installed
check_dependencies()
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tqdm import tqdm

class StorageHistoryTracker:
    """
    Tracks and visualizes storage usage across project folders on network drives.
    
    This class scans specified drives, collects folder size data, maintains a history
    of folder sizes over time, and generates interactive visualizations to help
    identify storage patterns and potential areas of concern.
    """
    
    def __init__(self, drives=None, history_file=None):
        """
        Initialize the tracker with specified drives and history file.
        
        Args:
            drives (list): List of drive letters to scan (default: ['I', 'J'])
            history_file (str): Path to history storage file (default: 'storage_history.json')
        """
        self.drives = drives or ['I', 'J']
        self.history_file = history_file or 'storage_history.json'
        self.history_data = self._load_history()
        self.date_today = datetime.now().strftime('%Y-%m')
        self.min_folder_size_gb = 1.0  # Only track folders larger than this size
        self.folder_timeout = 120  # Allow up to 2 minutes per folder
        self.failed_folders = []  # Track failed folders for each scan
    
    def _load_history(self):
        """
        Load the storage history data from file.
        
        Returns:
            dict: Dictionary containing storage history by drive and date
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            else:
                logging.info("History file not found. Creating new history data.")
                return {drive: {} for drive in self.drives}
        except Exception as e:
            logging.error(f"Error loading history data: {str(e)}")
            return {drive: {} for drive in self.drives}
    
    def _save_history(self):
        """Save the storage history data to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2)
            logging.info(f"History data saved to {self.history_file}")
        except Exception as e:
            logging.error(f"Error saving history data: {str(e)}")
    
    def get_folder_size_with_timeout(self, folder_path, timeout=60):
        """
        Calculate the total size of a folder with timeout.
        
        Args:
            folder_path (str): Path to the folder
            timeout (int): Maximum time in seconds to spend on this folder
            
        Returns:
            float: Size in bytes or 0 if an error or timeout occurs
        """
        # Create a queue to get the result from the thread
        result_queue = queue.Queue()
        folder_name = os.path.basename(folder_path)
        
        # Worker function to calculate folder size
        def calculate_size():
            try:
                total_size = 0
                if not os.path.exists(folder_path):
                    result_queue.put(0)
                    return
                    
                try:
                    # Simplified folder size calculation to avoid recursion issues
                    for subpath, dirs, files in os.walk(folder_path):
                        for file in files:
                            try:
                                file_path = os.path.join(subpath, file)
                                total_size += os.path.getsize(file_path)
                            except (PermissionError, OSError):
                                continue
                        
                except (PermissionError, OSError) as e:
                    logging.warning(f"Permission error scanning {folder_path}: {str(e)}")
                    
                result_queue.put(total_size)
            except Exception as e:
                logging.error(f"Error calculating size for {folder_path}: {str(e)}")
                result_queue.put(0)
        
        # Start worker thread
        worker = threading.Thread(target=calculate_size)
        worker.daemon = True
        worker.start()
        
        # Wait for result with timeout
        try:
            result = result_queue.get(timeout=timeout)
            return result
        except queue.Empty:
            logging.warning(f"Timeout calculating size for {folder_path} after {timeout} seconds")
            print(f"\nSkipping folder {folder_name} due to timeout - it may be too large to process efficiently")
            return 0
    
    def scan_drive(self, drive_letter):
        """
        Scan a drive for folder sizes.
        
        Args:
            drive_letter (str): Drive letter to scan (e.g., 'I')
            
        Returns:
            dict: Dictionary of folder paths and sizes in GB
        """
        drive_path = f"{drive_letter}:\\"
        folder_sizes = {}
        self.failed_folders = []  # Reset for each drive
        
        logging.info(f"Scanning drive {drive_letter}...")
        print(f"\nScanning drive {drive_letter}... (This may take a while)")
        
        try:
            if not os.path.exists(drive_path):
                logging.error(f"Drive {drive_path} not found")
                return folder_sizes
            
            # Get all top-level folders
            try:
                top_folders = [f for f in os.listdir(drive_path) 
                              if os.path.isdir(os.path.join(drive_path, f))]
            except Exception as e:
                logging.error(f"Error listing folders on drive {drive_letter}: {str(e)}")
                return folder_sizes
            
            # Process folders with progress bar
            for i, folder_name in enumerate(top_folders):
                folder_path = os.path.join(drive_path, folder_name)
                
                # Display progress update
                progress = (i + 1) / len(top_folders) * 100
                print(f"\rProgress: {progress:.1f}% | Scanning: {folder_name[:30]}{'...' if len(folder_name) > 30 else ''}       ", end='')
                
                if os.path.isdir(folder_path):
                    start_time = time.time()
                    size_bytes = self.get_folder_size_with_timeout(folder_path, self.folder_timeout)
                    elapsed = time.time() - start_time
                    
                    if size_bytes == 0:
                        self.failed_folders.append(folder_name)
                        logging.warning(f"Failed to scan folder (timeout or error): {folder_name}")
                        print(f"\nFailed to scan folder (timeout or error): {folder_name}")
                        continue
                    
                    size_gb = size_bytes / (1024 ** 3)  # Convert to GB
                    
                    # Only track folders larger than threshold
                    if size_gb >= self.min_folder_size_gb:
                        folder_sizes[folder_name] = size_gb
                        logging.info(f"Folder: {folder_name}, Size: {size_gb:.2f} GB (scanned in {elapsed:.1f}s)")
                        print(f"\nFound large folder: {folder_name} - {size_gb:.2f} GB")
            
            print(f"\nFinished scanning drive {drive_letter}: Found {len(folder_sizes)} folders over {self.min_folder_size_gb}GB")
            if self.failed_folders:
                print(f"\nWARNING: {len(self.failed_folders)} folders could not be scanned in time and were skipped:")
                for ff in self.failed_folders:
                    print(f"  - {ff}")
                logging.warning(f"{len(self.failed_folders)} folders failed to scan on drive {drive_letter}")
        
        except Exception as e:
            logging.error(f"Error scanning drive {drive_letter}: {str(e)}")
        
        return folder_sizes
    
    def update_history(self):
        """
        Scan all drives and update the history data with current folder sizes.
        """
        print("\nUpdating storage history for specified drives...")
        
        for drive in self.drives:
            logging.info(f"Processing drive {drive}...")
            print(f"\n{'='*20} DRIVE {drive}: {'='*20}")
            
            # Create entry for current date if it doesn't exist
            if self.date_today not in self.history_data[drive]:
                self.history_data[drive][self.date_today] = {}
            
            # Scan the drive and update history
            folder_sizes = self.scan_drive(drive)
            self.history_data[drive][self.date_today] = folder_sizes
            
            # Save after each drive in case of interruption
            self._save_history()
            print(f"History for drive {drive} updated and saved")
        
        print("\nHistory update completed successfully!")
        logging.info("History update completed")
    
    def generate_visualizations(self, output_dir="storage_reports"):
        """
        Generate interactive visualizations for folder size history.
        
        Args:
            output_dir (str): Directory to save the generated HTML files
        
        Returns:
            list: Paths to the generated HTML files
        """
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        html_files = []
        print("\nGenerating interactive visualizations...")
        
        for drive in self.drives:
            try:
                logging.info(f"Generating visualization for drive {drive}...")
                print(f"Creating visualization for drive {drive}...")
                
                # Convert history data to DataFrame
                data = []
                for date, folder_sizes in self.history_data[drive].items():
                    for folder, size in folder_sizes.items():
                        data.append({
                            'date': date,
                            'folder': folder,
                            'size_gb': size
                        })
                
                if not data:
                    logging.warning(f"No data available for drive {drive}")
                    print(f"No data available for drive {drive}, skipping visualization")
                    continue
                
                df = pd.DataFrame(data)
                
                # Create interactive plot with plotly
                fig = make_subplots(rows=1, cols=1, subplot_titles=[f"Storage History for Drive {drive}:"])
                
                # Get unique folders and create a trace for each
                folders = df['folder'].unique()
                
                # For each folder, create a line trace
                for folder in sorted(folders):
                    folder_data = df[df['folder'] == folder]
                    
                    # Convert dates to datetime for proper ordering
                    folder_data['date'] = pd.to_datetime(folder_data['date'])
                    folder_data = folder_data.sort_values('date')
                    
                    # Create line trace
                    fig.add_trace(
                        go.Scatter(
                            x=folder_data['date'],
                            y=folder_data['size_gb'],
                            mode='lines+markers',
                            name=folder,
                            hovertemplate='<b>%{x}</b><br>Size: %{y:.2f} GB<extra></extra>'
                        )
                    )
                
                # Customize layout
                fig.update_layout(
                    title_text=f"Project Folder Size History - Drive {drive}:",
                    xaxis_title="Date",
                    yaxis_title="Size (GB)",
                    height=800,
                    legend_title="Project Folders",
                    hovermode="closest",
                    template="plotly_dark",
                    margin=dict(l=50, r=50, t=100, b=50),
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        bgcolor="rgba(50, 50, 50, 0.7)",
                        bordercolor="rgba(200, 200, 200, 0.7)",
                        borderwidth=1
                    ),
                    updatemenus=[
                        dict(
                            buttons=[
                                dict(
                                    args=[{"visible": [True] * len(folders)}],
                                    label="Show All",
                                    method="update"
                                ),
                                dict(
                                    args=[{"visible": [False] * len(folders)}],
                                    label="Hide All",
                                    method="update"
                                )
                            ],
                            direction="down",
                            pad={"r": 10, "t": 10},
                            showactive=True,
                            x=0.98,
                            xanchor="right",
                            y=1.15,
                            yanchor="top"
                        )
                    ],
                    annotations=[
                        dict(
                            text="Filter:",
                            x=0.915,
                            y=1.15,
                            xref="paper",
                            yref="paper",
                            showarrow=False
                        )
                    ]
                )
                
                # Add growth rate calculation
                if len(df['date'].unique()) > 1:
                    # Calculate growth rate for each folder
                    growth_info = []
                    for folder in folders:
                        folder_data = df[df['folder'] == folder].sort_values('date')
                        if len(folder_data) >= 2:
                            dates = pd.to_datetime(folder_data['date'])
                            oldest_date = dates.min()
                            newest_date = dates.max()
                            
                            oldest_size = folder_data[folder_data['date'] == oldest_date]['size_gb'].values[0]
                            newest_size = folder_data[folder_data['date'] == newest_date]['size_gb'].values[0]
                            
                            # Calculate days between
                            days_diff = (newest_date - oldest_date).days
                            if days_diff > 0:
                                growth_gb = newest_size - oldest_size
                                growth_rate = growth_gb / days_diff  # GB per day
                                
                                if growth_rate > 0:
                                    growth_info.append(f"{folder}: {growth_rate:.3f} GB/day")
                    
                    if growth_info:
                        fig.add_annotation(
                            text="<b>Folders with highest growth rate:</b><br>" + "<br>".join(sorted(growth_info, reverse=True)[:5]),
                            x=0.98,
                            y=0.05,
                            xref="paper",
                            yref="paper",
                            showarrow=False,
                            align="right",
                            bgcolor="rgba(50, 50, 50, 0.7)",
                            bordercolor="rgba(200, 200, 200, 0.7)",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    
                    fig.add_annotation(
                        text="<b>Hover over lines to see growth trends</b>",
                        x=0.5,
                        y=1.06,
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=12)
                    )
                
                # Add range slider for time selection
                fig.update_xaxes(
                    rangeslider_visible=True,
                    rangeselector=dict(
                        buttons=list([
                            dict(count=3, label="3m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    )
                )
                
                # Save the figure as an HTML file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                html_file = os.path.join(output_dir, f"drive_{drive}_history_{timestamp}.html")
                fig.write_html(html_file, include_plotlyjs="cdn")
                
                html_files.append(html_file)
                logging.info(f"Visualization saved to {html_file}")
                print(f"Visualization saved to {html_file}")
            
            except Exception as e:
                logging.error(f"Error generating visualization for drive {drive}: {str(e)}")
                print(f"Error generating visualization for drive {drive}: {str(e)}")
        
        print(f"\nVisualizations generated successfully in folder: {os.path.abspath(output_dir)}")
        return html_files
        
    def open_visualizations(self, html_files):
        """
        Open the generated HTML files in the default browser.
        
        Args:
            html_files (list): List of HTML file paths to open
        """
        if html_files:
            print(f"\nOpening {len(html_files)} interactive visualization(s) in your browser...")
            
        for html_file in html_files:
            try:
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
                print(f"- Opened: {os.path.basename(html_file)}")
            except Exception as e:
                logging.error(f"Error opening visualization: {str(e)}")


def main():
    """Main function to run the storage history tracker."""
    try:
        print("=" * 80)
        print("STORAGE HISTORY TRACKER".center(80))
        print("=" * 80)
        print("This tool helps identify large or rapidly growing project folders on network drives.\n")
        logging.info("Starting Storage History Tracker")
        
        # Create tracker instance
        tracker = StorageHistoryTracker()
        
        # Check if drives exist before proceeding
        drives_available = []
        for drive in tracker.drives:
            drive_path = f"{drive}:\\"
            if os.path.exists(drive_path):
                drives_available.append(drive)
                print(f"✓ Drive {drive}: detected")
            else:
                logging.warning(f"Drive {drive_path} not found, skipping")
                print(f"✗ Drive {drive}: not found")
        
        if not drives_available:
            logging.error("No specified drives are available. Exiting.")
            print("\nERROR: None of the specified drives (I:, J:) are available.")
            print("Please check your network connections and try again.")
            return 1
        
        # Update tracker with available drives
        tracker.drives = drives_available
        
        # Update history data
        logging.info("Scanning drives and updating history...")
        tracker.update_history()
        
        # Generate and open visualizations
        logging.info("Generating visualizations...")
        html_files = tracker.generate_visualizations()
        
        if html_files:
            logging.info(f"Opening {len(html_files)} visualization(s) in browser...")
            tracker.open_visualizations(html_files)
        else:
            logging.warning("No visualizations were generated")
            print("\nWARNING: No visualizations were generated. Check the log file for details.")
            
        print("\nStorage History Tracker completed successfully!")
        print("-" * 80)
        print("Tip: Run this script periodically to build up history data and track growth trends.")
        print("-" * 80)
        
        logging.info("Storage History Tracker completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"\nERROR: {str(e)}")
        print("Check the log file (drive_history_tracker.log) for more details.")
        return 1
    
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting gracefully...")
        print("Note: Some data may have been saved before interruption.")
        logging.info("Process interrupted by user")
        return 0
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
