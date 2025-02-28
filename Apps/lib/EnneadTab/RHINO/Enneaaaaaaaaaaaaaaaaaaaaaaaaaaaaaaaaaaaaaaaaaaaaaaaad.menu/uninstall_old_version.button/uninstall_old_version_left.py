
__title__ = "UninstallOldVersion"
__doc__ = """Uninstall old version of EnneadTab. Do this only if you have old enneadtab for rhino on your machine.

"""
__FONDATION__ = True


import rhinoscriptsyntax as rs

def uninstall_old_version():
    res = rs.MessageBox(__doc__, 1)
    if res == 2:
        return

    for toolbar_collection in rs.ToolbarCollectionNames():
        if "EnneadTab" == toolbar_collection:
            rs.CloseToolbarCollection(toolbar_collection)

    for path in rs.SearchPathList():
        if "EnneadTab".lower() in path.lower():
            rs.DeleteSearchPath(path)

    rs.MessageBox("Restart your rhino before install the new version.")

    
if __name__ == "__main__":
    uninstall_old_version()
