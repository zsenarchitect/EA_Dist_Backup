


import publish_revit
import publish_rhino
import sync_core_module

def main():
    sync_core_module.main()
    publish_rhino.main()
    publish_revit.main()


if __name__ == "__main__":
    main()