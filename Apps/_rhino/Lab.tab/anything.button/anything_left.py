
__title__ = "Anything"
__doc__ = "This button does Anything, depedening what you want to quickly test without creating a new button"


from EnneadTab import ERROR_HANDLE, LOG, VERSION_CONTROL

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def anything():
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))

    VERSION_CONTROL.updater_for_shanghai()


    
if __name__ == "__main__":
    anything()
