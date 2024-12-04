
__title__ = "AppStore"
__doc__ = "Open the all apps avaibalie for enneadtab"


from EnneadTab import ERROR_HANDLE, LOG, EXE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def app_store():
    EXE.try_open_app("AppStore", safe_open=True)
    
if __name__ == "__main__":
    app_store()
