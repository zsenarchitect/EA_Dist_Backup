__title__ = "See You Again"
__doc__ = """Smart session scheduler that prepares your Revit environment for your next work session. 

This time-saving utility allows you to:
- Schedule your current Revit files to reopen automatically
- Choose when they reopen: in minutes, tomorrow morning, or next Monday
- Skip the lengthy file loading process when you return to work
- Maintain your exact workspace configuration between sessions

Perfect for teams working with large projects that take significant time to open each day."""


__tip__ = True
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_SYNC
from EnneadTab import EXE, DATA_FILE, NOTIFICATION, USER, ERROR_HANDLE, LOG, ENVIRONMENT
from pyrevit import forms, script
# import datetime
from datetime import datetime, timedelta
# https://pypi.org/project/tkTimePicker/
# time picker

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    # if ENVIRONMENT.IS_AVD:
    #     NOTIFICATION.duck_pop("If you log off AVD, this will not reopen new session for you.")
    # get all open docs
    docs = REVIT_APPLICATION.get_app().Documents
    docs = [doc for doc in docs if not doc.IsLinked]
    docs = [doc.Title for doc in docs if not doc.IsFamilyDocument]

    data_file = "schedule_opener_data.sexyDuck"

    data = DATA_FILE.get_data(data_file)
        
    if data is None:
        data = dict()

    data["revit_version"] = REVIT_APPLICATION.get_app().VersionNumber
    recorded_docs = data.get("docs", [])
    for doc in docs:
        recorded_docs.append(doc)
    data["docs"] = list(set(recorded_docs))

    options = ["Tomorrow Morning 7am",
               "Tomorrow Morning 8am",
               "Tomorrow Morning 9am",
               "Next Monday Morning 7am",
               "In 5 Mins",               
               "In 2 Mins"]
    schedule_time = forms.ask_for_one_item(prompt="When to reopen current openned documents?",
                                  items = options,title = "EnneadTab See You Soon!",
                                  default = options[0])
    if schedule_time == options[0]:
        schedule_time = get_date(clock=7, is_tomorrow=True, is_next_week=False)
    elif schedule_time == options[1]:
        schedule_time = get_date(8,True, False)
    elif schedule_time == options[2]:
        schedule_time = get_date(9,True, False)
    elif schedule_time == options[3]:
        schedule_time = get_date(7, False, True)
    elif schedule_time == options[4]:
        schedule_time = datetime.now() + timedelta(minutes = 5.0)
    elif schedule_time == options[5]:
        schedule_time = datetime.now() + timedelta(minutes = 2.0)
    else:
        return
    data["open_time"] = schedule_time.isoformat()
    res = DATA_FILE. set_data(data, data_file)
    # print (res)
    
    
    

    EXE.try_open_app("ScheduleOpener")
        
    REVIT_SYNC.sync_and_close()
    
    import time
    time.sleep(5)
    REVIT_SYNC.sync_and_close()
    REVIT_APPLICATION.close_revit_app()
    REVIT_FORMS.notification(main_text = "There is nothing to see here. Close this revit.",
                                             sub_text = "Your scheduled reopen revit file will show up in new session.")



def get_date(clock,is_tomorrow, is_next_week):
    # Get the current date and time
    now = datetime.now()


    if is_next_week: 
        # Calculate the number of days until the next Monday
        days_until_next_monday = (7 - now.weekday()) % 7 or 7  # if today is Monday, then get the next Monday

        # Get the date for the next Monday
        target_day = now + timedelta(days=days_until_next_monday)

    if is_tomorrow:
        # Calculate tomorrow's date
        target_day = now + timedelta(days=1)

    # Get 7 a.m. of tomorrow's date
    return datetime(target_day.year, target_day.month, target_day.day, clock, 0)



######################################################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()
