
__title__ = "GetEngine"
__doc__ = "Ensure that you have a localized Python engine installed"


from EnneadTab import ERROR_HANDLE, LOG, EXE
reload(EXE)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_engine():
    EXE.ensure_engine_installed()

    EXE.cast_python("EnneadTab_OS_Installer")
    
if __name__ == "__main__":
    get_engine()
