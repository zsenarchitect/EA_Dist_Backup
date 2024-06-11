import publish_revit
import publish_rhino
import sync_core_module
import time

def publish_both():
    start = time.time()
    sync_core_module.sync_core()
    publish_revit.publish_revit()
    publish_rhino.publish_rhino()

    end_time = time.time()
    print ("\n\n\nFinish in {}s".format(end_time - start))


if __name__ == "__main__":
    publish_both()