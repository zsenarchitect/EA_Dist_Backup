__title__ = "AppStore"
__doc__ = """EnneadTab App Store launcher.

Access the complete collection of EnneadTab tools and utilities
through a centralized application store interface."""


from EnneadTab import ERROR_HANDLE, LOG, EXE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def app_store():
    EXE.try_open_app("AppStore", safe_open=True)
    
if __name__ == "__main__":
    app_store()
