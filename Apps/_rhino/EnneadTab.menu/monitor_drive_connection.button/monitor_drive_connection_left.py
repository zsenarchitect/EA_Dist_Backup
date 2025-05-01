__title__ = "MonitorDriveConnection"
__doc__ = """Launches the MonitorDrive application to track and manage network drive connections.
This tool provides real-time monitoring of network drive status and connection health."""


from EnneadTab import ERROR_HANDLE, LOG, EXE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def monitor_drive_connection():
    EXE.try_open_app("MonitorDrive")

    
if __name__ == "__main__":
    monitor_drive_connection()
