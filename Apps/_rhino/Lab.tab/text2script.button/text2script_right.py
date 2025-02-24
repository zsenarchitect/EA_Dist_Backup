
__title__ = "Text2ScriptSetting"
__doc__ = "This button does Text2ScriptSetting when right click"


from EnneadTab import ERROR_HANDLE, LOG

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def text2script_setting():
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))

    
if __name__ == "__main__":
    text2script_setting()
