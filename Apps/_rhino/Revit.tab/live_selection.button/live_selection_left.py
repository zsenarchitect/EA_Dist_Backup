
__title__ = "LiveSelection"
__doc__ = "This button does LiveSelection when left click"


from EnneadTab import ERROR_HANDLE, LOG

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def live_selection():
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))

    
if __name__ == "__main__":
    live_selection()
