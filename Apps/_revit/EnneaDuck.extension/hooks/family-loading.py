
"""
store session script data to a temp file
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/appdata.html


share parameter between script
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/envvars.html
"""

import io
from pyrevit import script
from pyrevit import EXEC_PARAMS
# from pyrevit.coreutils import appdata
from pyrevit.coreutils import envvars
import time
import pickle
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_EVENT
envvars.set_pyrevit_env_var("FAMILY_LOAD_BEGIN", time.time())
datafile = script.get_instance_data_file("sub_c_list")

# print datafile


def get_subc(category):
    temp = []
    for c in category:
        for sub_c in c.SubCategories:
            temp.append("[{0}]--->[{1}]".format(c.Name, sub_c.Name))
    return temp

def main():
    if not REVIT_EVENT.is_family_load_hook_enabled():
        return
    doc = EXEC_PARAMS.event_args.Document

    all_Cs = doc.Settings.Categories

    data = get_subc(all_Cs)

    f = io.open(datafile, 'w', encoding="utf-8")
    pickle.dump(data, f)
    f.close()
############### main ###################
if __name__ == "__main__":
    main()


