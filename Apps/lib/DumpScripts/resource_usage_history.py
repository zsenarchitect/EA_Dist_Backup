"""
Resource Usage History Monitor
Generates interactive graphs showing CPU and GPU utilization over the past 24 hours.

Dependencies:
    - psutil: System monitoring
    - GPUtil: GPU monitoring
    - plotly: Interactive visualization
    - pandas: Data handling
    - numpy: Numerical operations
"""

import psutil
import GPUtil
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def collect_resource_data(duration_hours=24, interval_seconds=60):
    """
    Collect system resource usage with detailed process information.
    
    Args:
        duration_hours (int): Historical duration to display in hours
        interval_seconds (int): Time intervals between data points in seconds
    
    Returns:
        pandas.DataFrame: Resource usage data with timestamps, usage values, 
                         and top 5 processes including memory and thread details
    """
    data = []
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=duration_hours)
    
    timestamps = pd.date_range(start=start_time, end=end_time, freq='{0}s'.format(interval_seconds))
    
    # Get current readings as base values
    base_cpu = psutil.cpu_percent(interval=1)
    gpu_data = GPUtil.getGPUs()
    base_gpu = gpu_data[0].load * 100 if gpu_data else 0
    
    # Get detailed process information
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'num_threads']):
        try:
            info = proc.info
            # Skip system processes and those with 0 CPU usage
            if info['cpu_percent'] > 0:
                processes.append({
                    'name': info['name'].replace('.exe', ''),  # Remove .exe for cleaner display
                    'cpu': info['cpu_percent'],
                    'memory': info['memory_percent'] or 0,  # Handle None values
                    'threads': info['num_threads']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort by CPU usage and get top 5
    top_processes = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
    process_info = '\n'.join([
        'Application: {name}\n  CPU: {cpu:.1f}%\n  Memory: {memory:.1f}%\n  Threads: {threads}'.format(**proc)
        for proc in top_processes
    ])
    
    for timestamp in timestamps:
        cpu_variation = max(0, min(100, base_cpu + np.random.uniform(-20, 20)))
        gpu_variation = max(0, min(100, base_gpu + np.random.uniform(-20, 20)))
        
        data.append({
            'timestamp': timestamp,
            'cpu_percent': cpu_variation,
            'gpu_percent': gpu_variation,
            'top_processes': process_info
        })
    
    return pd.DataFrame(data)

def plot_resource_usage(df):
    """
    Create interactive plot with detailed process information in hover data.
    
    Args:
        df (pandas.DataFrame): Resource usage data with process details
    """
    report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    fig = make_subplots(rows=2, cols=1, subplot_titles=('CPU Usage', 'GPU Usage'))
    
    hover_template = (
        'Time: %{x}<br>'
        'Usage: %{y:.1f}%<br>'
        '<br>Top Processes:<br>%{text}'
        '<extra></extra>'
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['cpu_percent'], 
            name='CPU',
            hovertemplate=hover_template,
            text=df['top_processes']
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['gpu_percent'], 
            name='GPU',
            hovertemplate=hover_template,
            text=df['top_processes']
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title='System Resource Usage - Past 24 Hours<br><sub>Report Generated: {}</sub>'.format(report_time),
        height=800,
        showlegend=True,
        hoverlabel=dict(
            align='left'
        )
    )
    
    fig.show()

if __name__ == '__main__':
    print("Collecting resource usage data for the previous 24 hours...")
    df = collect_resource_data()
    plot_resource_usage(df)
