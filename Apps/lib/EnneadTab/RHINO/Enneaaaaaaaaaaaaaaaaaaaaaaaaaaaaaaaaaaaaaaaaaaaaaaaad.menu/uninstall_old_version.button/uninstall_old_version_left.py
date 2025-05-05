
__title__ = "UninstallOldVersion"
__doc__ = """Uninstall any version of EnneadTab. Do this only if you have old enneadtab for rhino on your machine.

"""
__FONDATION__ = True


import rhinoscriptsyntax as rs

def uninstall_old_version():
    print ("###################")
    res = rs.MessageBox(__doc__, 1)
    if res == 2:
        return

    for toolbar_collection in rs.ToolbarCollectionNames():
        if "ennead".lower() in toolbar_collection.lower():
            rs.CloseToolbarCollection(toolbar_collection)

    for path in rs.SearchPathList():
        if "ennead".lower() in path.lower():
            rs.DeleteSearchPath(path)

    rs.MessageBox("Restart your rhino.")


if __name__ == "__main__":
    uninstall_old_version()
 