
__title__ = "QuickTestTemp"
__doc__ = "This button does QuickTestTemp when left click"


from EnneadTab import ERROR_HANDLE, LOG, TIMESHEET

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def quick_test_temp():
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))
    TIMESHEET.print_timesheet_detail()

    TIMESHEET.update_timesheet("test rhino")    
if __name__ == "__main__":
    quick_test_temp()
