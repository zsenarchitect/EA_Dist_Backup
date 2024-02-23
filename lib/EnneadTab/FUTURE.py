

import USER_CONSTANTS
import random 

note = """
Here are some unfinished projects.... fin d a time to do them
    - Miro Listener
    - Design Room
    - redo Rhino rui system
    - git2updater for rhino
    - crv2road
    - base conduit
    - use threading to make own hook about pop ask if want to place new crated view at sheet(The is no post command hook so use this to monitor the creation of new view)
"""
if USER_CONSTANTS.USER_NAME == "szhang" and random.random() < 0.1:
    print (note)