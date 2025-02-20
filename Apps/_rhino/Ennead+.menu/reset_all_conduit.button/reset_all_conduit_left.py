__title__ = "ResetAllConduit"
__doc__ = """Reset all display conduits to default state.

Key Features:
- Complete conduit cleanup
- Memory optimization
- Display pipeline reset
- System performance improvement
- Debug assistance"""

import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def reset_all_conduit():
    print ("current stickys")
    print (sc.sticky.items())

    for key in sc.sticky.keys():
        if "conduit" in key.lower():
            conduit = sc.sticky[key]
            print ("removing sticky:" + key)

            # some old key also has conduit in name, but not as actal conduit obj
            if hasattr(conduit, "Enabled"):
                conduit.Enabled = False
            sc.sticky.pop(key)



if __name__ == "__main__":
    reset_all_conduit()