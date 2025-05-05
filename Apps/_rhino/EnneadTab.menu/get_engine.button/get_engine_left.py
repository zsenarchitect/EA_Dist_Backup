__title__ = "GetEngine"
__doc__ = "Ensure that you have a localized Python engine installed"


import sys
import os
# Add proper path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Use proper import syntax
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab import ENGINE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_engine():
    ENGINE.ensure_engine_installed()

    
if __name__ == "__main__":
    get_engine()
