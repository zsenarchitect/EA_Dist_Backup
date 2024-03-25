


import publish_revit
import publish_rhino
import sync_core_module

def publish_both():
    sync_core_module.sync_core()
    publish_rhino.publish_rhino()
    publish_revit.publish_revit()


if __name__ == "__main__":
    publish_both()