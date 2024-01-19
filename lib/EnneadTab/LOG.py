import os
import time
import json
import USER_CONSTANTS
import DATA_FILE
import ENVIRONMENT_CONSTANTS
import TIME
import OUTPUT
import FOLDER


from contextlib import contextmanager

@contextmanager
def log_usage(func,*args):
    t_start = time.time()
    res = func(*args)
    yield res
    t_end = time.time()
    duration = TIME.get_readable_time(t_end - t_start)
    with open(get_log_file(), "a") as f:
        f.writelines('\nRun at {}'.format(TIME.get_formatted_time(t_start)))
        f.writelines('\nDuration: {}'.format(duration))
        f.writelines('\nFunction name: {}'.format(func.__name__))
        f.writelines('\nArguments: {}'.format(args))
        f.writelines('\nResult: {}'.format(res))
    """
    also log here some info on the usage status. Make a context manager
    when:
    who:
    duration:
    file_name:
    error, if any:
    """

# with log_usage(get_log_file()) as f:
#     f.writelines('\nYang is writing!')

    


        
def get_log_folder():
    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        log_folder = ENVIRONMENT_CONSTANTS.REVIT_USER_LOG_FOLDER
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        log_folder = ENVIRONMENT_CONSTANTS.RHINO_USER_LOG_FOLDER
    if "log_folder" not in locals():
        log_folder = "{}\LOG".format(FOLDER.get_EA_setting_folder())
        os.makedirs(log_folder, exist_ok = True)
    return log_folder


def get_log_file(user_name = None):
    log_folder = get_log_folder()
    if not user_name:
        user_name = USER_CONSTANTS.USER_NAME
    return "{}\{}.json".format(log_folder, user_name)

def log(script_path, func_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log_file = get_log_file()


            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    data = dict()
                    data["personal_data"] = {"name": USER_CONSTANTS.USER_NAME}
                    data["log"] = {}
                    json.dump(data, f)

            with open(log_file, "r") as f:
                data = json.load(f)


            
            t_start = time.time()
            out = func(*args, **kwargs)
            t_end = time.time()
            
            # print (func.__name__)

            data["log"][TIME.get_formatted_current_time()] = {"function_name": func_name,
                                                                "arguments": args,
                                                                "result": out,
                                                                "script_path": script_path,
                                                                "duration": TIME.get_readable_time(t_end - t_start)
                                                                }

            with open(log_file, "w") as f:
                json.dump(data, f)
  
            return out
        return wrapper
    return decorator





def read_log(user_name = USER_CONSTANTS.USER_NAME):
    log_file = get_log_file(user_name)
    with open(log_file, "r") as f:
        data = json.load(f)


    print ("Printing user log from <{}>".format(user_name))
    import pprint
    pprint.pprint(data, indent= 4)



########################### TimeSheet related ################################
TIMESHEET_HELPER_FILE = "TIMESHEET.json"
IS_UNIVERSAL_STORAGE_PREFERED = USER_CONSTANTS.USER_NAME in ["szhang"]

def update_time_sheet_revit(doc_name):
    update_time_sheet_by_software(doc_name, "revit")
    
def update_time_sheet_rhino(doc_name):
    update_time_sheet_by_software(doc_name, "rhino")

def update_time_sheet_by_software(doc_name, software):
    
    data = get_time_sheet_data()
    software_data = data.get(software, {})
    today = time.strftime("%Y-%m-%d")
    today_data = software_data.get(today, {})
    current_doc_data = today_data.get(doc_name, {})
    if "starting_time" not in current_doc_data:
        current_doc_data["starting_time"] = time.time()
    current_doc_data.update({"end_time": time.time()})
    today_data[doc_name] = current_doc_data
    software_data[today] = today_data
    data[software] = software_data
    if IS_UNIVERSAL_STORAGE_PREFERED:
        DATA_FILE.save_dict_to_json_in_shared_dump_folder(data, TIMESHEET_HELPER_FILE.replace(".json", "_{}.json".format(USER_CONSTANTS.USER_NAME)))
    else:
        DATA_FILE.save_dict_to_json_in_dump_folder(data, TIMESHEET_HELPER_FILE)
    

def print_time_sheet_detail():
    def print_in_style(text):
    
        if ENVIRONMENT_CONSTANTS.is_Revit_environment():
            from pyrevit import script
            output = script.get_output()
            lines = text.split("\n")
            for line in lines:
                output.print_md(line)
            return
        
        print (text)
        
            
    
    
    output = ""
    data = get_time_sheet_data()
    for software in ["revit", "rhino"]:
        output +="\n\n"
        output +=  ("\n# Printing time sheet for {}".format(software.capitalize()))
        log_data = data.get(software, {})
        for date, doc_data in sorted( log_data.items()):
            output += ("\n## Date: {}".format(date))
            for doc_name, doc_info in doc_data.items():
                output += ("\n### Doc Name: {}".format(doc_name))
                starting_time = doc_info.get("starting_time", None)
                end_time = doc_info.get("end_time", None)
                
                duration = end_time - starting_time
                if duration < 2:
                    output += ("\n    - Open Time: {}".format(TIME.get_formatted_time(starting_time)))
                    
                else:
                    if starting_time and end_time:
                        output += ("\n    - Starting Time: {}".format(TIME.get_formatted_time(starting_time)))
                        output += ("\n    - End Time: {}".format(TIME.get_formatted_time(end_time)))
                        output += ("\n    - Duration: {}".format(TIME.get_readable_time(duration)))
              
            output += ("\n")
    

            
    output += ("\n\n\nOutput finish!\nIf you are not seeing the record as wished for Rhino files, please 'GetLatest' from menu and follow instruction on Email.")

    if ENVIRONMENT_CONSTANTS.is_Revit_environment() and USER_CONSTANTS.is_enneadtab_developer():
        print_revit_log_as_table()
    print_in_style (output)
    
    if ENVIRONMENT_CONSTANTS.is_Revit_environment():
        OUTPUT.display_output_on_browser()
    if ENVIRONMENT_CONSTANTS.is_Rhino_environment():
        import rhinoscriptsyntax as rs
        rs.TextOut(output)

def get_time_sheet_data():
    if IS_UNIVERSAL_STORAGE_PREFERED:
        data = DATA_FILE.read_json_as_dict_in_shared_dump_folder(TIMESHEET_HELPER_FILE.replace(".json", "_{}.json".format(USER_CONSTANTS.USER_NAME)), create_if_not_exist=True)
    else:
        data = DATA_FILE.read_json_as_dict_in_dump_folder(TIMESHEET_HELPER_FILE, create_if_not_exist=True)
    return data


def print_revit_log_as_table():
    # i am not doing this table for rhino becasue rhino file name are hard to identify which project it is.

    
    data = get_time_sheet_data()
    log_data = data.get("revit", {})
    # data = [
    # ['row1', 'data', 'data', 80 ],
    # ['row2', 'data', 'data', 45 ],
    # ]
    # >>> output.print_table(
    # table_data=data,
    # title="Example Table",
    # columns=["Row Name", "Column 1", "Column 2", "Percentage"],
    # formats=['', '', '', '{}%'],
    # last_line_style='color:red;'
    # )
    from pyrevit import script
    output = script.get_output()
    output.insert_divider()
    output.print_md("# This is a alternative display of the Revit Timesheet")
    table_data = []
    valiad_dates = set()
    proj_dict = dict()
    for date, doc_data in sorted( log_data.items()):
        valiad_dates.add(date)
        for doc_name, doc_info in doc_data.items():
            temp = proj_dict.get(doc_name, {})
            starting_time = doc_info.get("starting_time", None)
            end_time = doc_info.get("end_time", None)
            if starting_time and end_time:
                duration = end_time - starting_time
                temp[date] = duration
                proj_dict[doc_name] = temp

    for proj_name, proj_info in sorted(proj_dict.items()):
        total_duration = sum(proj_info.values())
        table_data.append([proj_name] + [TIME.get_readable_time(proj_info.get(date, 0)) if proj_info.get(date, 0) != 0 else "N/A" for date in sorted(valiad_dates)] + [TIME.get_readable_time(total_duration)])

    output.print_table(table_data=table_data,
                        title="Revit Timesheet",
                        columns=["Proj. Name"] + sorted(valiad_dates) + ["Total Hour"]
                        )

def unit_test():
    update_time_sheet_revit("test_project_revit_1")
    update_time_sheet_revit("test_project_revit_2")
    update_time_sheet_rhino("test_project_rhino_1")
    # print_time_sheet_detail()

    read_log()
    

    
    
###########################################################
if __name__ == "__main__":
    unit_test()