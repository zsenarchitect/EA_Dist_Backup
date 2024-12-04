
__title__ = "OpenEcosystemFolder"
__doc__ = "Open the Ecosystem folder."

import os
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_ecosystem_folder():
    os.startfile(ENVIRONMENT.ECO_SYS_FOLDER)


    
if __name__ == "__main__":
    open_ecosystem_folder()
