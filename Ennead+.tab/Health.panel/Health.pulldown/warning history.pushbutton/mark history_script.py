__doc__ = "Display/Write warning number history of the file.\n\nFor Bim360 project, publish project will introduce as new project title to track warnings"
__title__ = "Mark/Read\n Warning History"

from datetime import date
from pyrevit import forms, script, DB, revit
#from pyrevit.coreutils import appdata

import MARK_HISTORY

############ main code below #############
if __name__== "__main__":
    revit_name = str(revit.doc.Title)
    revit_name = MARK_HISTORY.name_fix(revit_name)

    file = script.get_universal_data_file(revit_name,file_ext = "txt")



    res = forms.alert(options = ["record warning to history",
                                "compare to lastest warning history",
                                "read all warning history"],
                                msg = "I want to [.....]")

    if "record" in res:
        warning_count = len(revit.doc.GetWarnings())
        data_entry = "{}:{}".format(date.today(), warning_count)
        MARK_HISTORY.append_data(file,data_entry)
    elif "most recent" in res:
        try:#becasue on opening do there will be a writing of today's data, so it is better to comare yesterday if it can
            last_item = MARK_HISTORY.read_data(file)[-2]
        except:
            last_item = MARK_HISTORY.read_data(file)[-1]
        warning_count = len(revit.doc.GetWarnings())
        print(MARK_HISTORY.compare_data(last_item,warning_count))

    elif "all" in res:
        all_history = MARK_HISTORY.read_data(file)
        for item in all_history:
            print(item)
        """
        for i in range(len(all_history)):
            print(MARK_HISTORY.compare_data(all_history[i]))
        """
    else:
        script.exit()
