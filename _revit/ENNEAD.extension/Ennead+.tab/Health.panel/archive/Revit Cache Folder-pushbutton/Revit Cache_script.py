__title__ = "Revit/Rhino\nCache Folder"
__context__ = 'zero-doc'

import os
import EA_UTILITY
import EnneadTab
import subprocess


path = r"{}\AppData\Local\Autodesk\Revit\PacCache".format(os.environ["USERPROFILE"])
EA_UTILITY.dialogue(main_text = "The cache in the upcoming folder 'C:\Users\YouName\AppData\Local\Autodesk\Revit' are all safe to delete. There are Crash journals, very old rvt links, unusaed locals, etc. from every version of Revit you have used.\n\n##BUT PLEASE DELETE THEM ONLY WHEN REVIT HAS BEEN CLOSED.##", sub_text = "You can delete those folders:\n  -Autodesk Revit 20xx\n  -PacCache\n\nNote:\nAfter Cache are deleted, you next Revit document openning will take longer than ususal because it will download cache again as needed.")

subprocess.Popen(r'explorer /select, {}'.format(path))


#C:\Users\szhang\AppData\Local\McNeel\Rhinoceros\temp
path = r"{}\AppData\Local\McNeel\Rhinoceros\temp".format(os.environ["USERPROFILE"])
EA_UTILITY.dialogue(main_text = "There are autosaves you might no longer need in the upcoming folder 'C:\Users\YouName\AppData\Local\McNeel\Rhinoceros' are safe to delete.\n\n##BUT PLEASE DELETE THEM ONLY WHEN RHINO HAS BEEN CLOSED.##", sub_text = "You can delete those folders:\n  -6.0\n  -7.0")

subprocess.Popen(r'explorer /select, {}'.format(path))
