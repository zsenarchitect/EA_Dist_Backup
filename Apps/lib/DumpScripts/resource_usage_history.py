"""
Resource Usage History Monitor
Generates interactive graphs showing CPU and GPU utilization over the past 24 hours.

Dependencies:
    - psutil: System monitoring
    - GPUtil: GPU monitoring
    - plotly: Interactive visualization
    - pandas: Data handling
"""

import psutil
import GPUtil
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time

def collect_resource_data(duration_hours=24, interval_seconds=60):
    """
    Collect system resource usage data for specified duration.
    
    Args:
        duration_hours (int): Duration to collect data in hours
        interval_seconds (int): Sampling interval in seconds
    
    Returns:
        pandas.DataFrame: Resource usage data with timestamps
    """
    data = []
    end_time = datetime.now() + timedelta(hours=duration_hours)
    
    while datetime.now() < end_time:
        timestamp = datetime.now()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        gpu_data = GPUtil.getGPUs()
        gpu_percent = gpu_data[0].load * 100 if gpu_data else 0
        
        data.append({
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'gpu_percent': gpu_percent
        })
        
        time.sleep(interval_seconds)
    
    return pd.DataFrame(data)

def plot_resource_usage(df):
    """
    Create interactive plot of resource usage.
    
    Args:
        df (pandas.DataFrame): Resource usage data
    """
    fig = make_subplots(rows=2, cols=1, subplot_titles=('CPU Usage', 'GPU Usage'))
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['cpu_percent'], name='CPU'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['gpu_percent'], name='GPU'),
        row=2, col=1
    )
    
    fig.update_layout(
        title='System Resource Usage - Past 24 Hours',
        height=800,
        showlegend=True
    )
    
    fig.show()

if __name__ == '__main__':
    print("Collecting resource usage data for the next 24 hours...")
    df = collect_resource_data()
    plot_resource_usage(df)
