__title__ = "OpenEcosystemFolder"
__doc__ = """Access the EnneadTab Ecosystem directory.

Key Features:
- Direct folder access
- System file management
- Resource exploration
- Configuration access
- Template management"""

import os
from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def open_ecosystem_folder():
    os.startfile(ENVIRONMENT.ECO_SYS_FOLDER)


    
if __name__ == "__main__":
    open_ecosystem_folder()
