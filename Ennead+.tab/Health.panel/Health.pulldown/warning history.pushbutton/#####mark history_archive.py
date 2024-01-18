__doc__ = "Depreciated"
__title__ = "Mark/Read\nHistory(Legacy)"

from datetime import date
from pyrevit import forms, script, DB, revit
#from pyrevit.coreutils import appdata
import pickle

def append_data(file,data_entry):

    try:
        f = open(file, 'r')
        current_data  = pickle.load(f)
        #print "get current data: {}".format(current_data)
        f.close()

        for item in current_data:
            if str(date.today()) in item:
                print "data with this date {} exist already".format(date.today())
                script.exit()


        f = open(file, 'w')

        current_data.append(data_entry)
        #print current_data
        #print "========="
        #print "dump new_data {}".format(current_data)
        pickle.dump(current_data, f)
        f.close()

    except:#no file exist yet so just create and write the first line
        #print "no file exist, making first line"
        f = open(file, 'w')
        pickle.dump([data_entry], f)
        #print "dump new_data {}".format(data_entry)
        f.close()


def read_data(file):
    try:
        f = open(file, 'r')
        current_data  = pickle.load(f)
        f.close()
    except:
        print "data with this file title {} do not exist".format(revit_name)
        script.exit()

    #print current_data



    #print "~~33333"
    """
    for line in current_data:
        print line
    """

    last_item = current_data[-1]
    print compare_data(last_item)

def compare_data(previous_data):
    old_date = previous_data.split(":")[0]
    old_warnings = int(previous_data.split(":")[1])
    warning_count = len(revit.doc.GetWarnings())
    warning_increase = warning_count - old_warnings
    percentage = "{:.1%}".format(abs(warning_increase/float(old_warnings)))
    if warning_increase > 0:
        text = "increased"
    elif warning_increase < 0:
        text = "decreased"
    else:
        return "The warning is {1}, the same number as on {0}".format(old_date, warning_count )
    return "Since {}, the warning has {} by {}.\nA change of {}%".format(old_date, text, abs(warning_increase), percentage )
############ main code below #############
if __name__== "__main__":
    #print date.today()


    #get curent revit central name
    revit_name = revit.doc.Title

    #check if data file with this name exist, if not:
        #make data file assocaited with this central
    #get data fiel with this name
    file = script.get_universal_data_file(revit_name,file_ext = "txt")
    #print file


    res = forms.alert(options = ["make history", "read history"], msg = "I want to [.....]")

    if "make" in res:
        warning_count = len(revit.doc.GetWarnings())
        data_entry = "{}:{}".format(date.today(), warning_count)
        #print data_entry
        #print "~~~~~"
        append_data(file,data_entry)
    elif "read" in res:
        read_data(file)
    else:
        script.exit()
