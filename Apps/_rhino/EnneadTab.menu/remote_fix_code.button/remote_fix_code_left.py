__title__ = "RemoteFixCode"
__doc__ = "Launches VS Code Dev for emergency remote code editing and debugging"


from EnneadTab import ERROR_HANDLE, LOG, CODE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def remote_fix_code():
    """Launch emergency code fix interface for remote debugging."""
    CODE.emergency_fix_code()

    
if __name__ == "__main__":
    remote_fix_code()
