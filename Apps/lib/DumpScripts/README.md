# One time wonder in IDE, not for everyday repeating use.

# EnneadTab DumpScripts

Collection of utility scripts for Ennead Architects.

## Storage History Tracker

The Storage History Tracker (`check_drive.py`) helps identify large and unused data on network drives by visualizing folder size trends over time.

### Features

- Scans I: and J: network drives to identify project folder sizes
- Tracks size history over time with persistent storage
- Generates interactive HTML visualizations showing size trends
- Helps identify rapidly growing folders that may need attention

### Usage

1. Run the script:
   ```
   python check_drive.py
   ```

2. The script will:
   - Scan the I: and J: drives for folder sizes
   - Update the history data file (`storage_history.json`)
   - Generate interactive HTML visualizations
   - Open the visualizations in your default browser

### Requirements

- Python 3.6+
- Dependencies: pandas, plotly, pathlib

You can install the required dependencies with:
```
pip install -r requirements.txt
```

### Tips for Using the Visualizations

- Use the interactive legend to hide/show specific project folders
- The time range selector lets you focus on specific time periods
- Hover over data points to see detailed size information
- Look for steep slopes which indicate rapid growth
- Filter the view to focus on the largest folders

### Notes

- The script only tracks folders above 1GB in size by default
- History is stored by month (YYYY-MM)
- First run will only show current sizes; subsequent runs will build history
- Use the generated log file for troubleshooting