
import sys
sys.path.append("..\lib")
import EnneadTab

"""
### TO-DO:
- Proposed functionality:
  - Design together like in a miro board.
  - Transfer content between team members.
  - Manage competition workflows.
#### Assigned to: **SZ**
"""

# ask for a room name, ---> meta file that store dict, key = username, value = Rhino file

# if not having a background file, assign one.

# ask if user wants to use a custom file to work on, if not give a empty rhino.

# set FPS for refresh rate, default 1 frame per second

# establish worksession connection with every file in the meta dict.(option to turn off by username)

# in a toggled display conduit, refresh all links session base on FPS setting.___maybe using external event is better
# R = rs.Command('-Worksession Save "{}" _Enter'.format(path))
# R = rs.Command('-Worksession Refresh _Enter')

# also in conduit, only export keyword layer and session in for performance reason.!!!!!!!!!!

# bake session file.

def toggle_design_room():
    pass

if __name__ == "__main__":
    toggle_design_room()
