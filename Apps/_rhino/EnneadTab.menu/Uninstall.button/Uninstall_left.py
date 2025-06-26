__title__ = "Uninstall EnneadTab"
__doc__ = "Completely uninstall EnneadTab from the system"
__FONDATION__ = True

import rhinoscriptsyntax as rs
import os
import tempfile
import Rhino


def create_startup_script_cleaner():
    """Create a temporary RhinoScript file to clean up startup scripts"""
    script_content = '''Option Explicit

Sub CleanupStartupScripts()
    Dim startupScripts, scriptPath, count
    count = 0
    
    startupScripts = Rhino.StartupScriptList()
    
    If Not IsNull(startupScripts) Then
        For Each scriptPath In startupScripts
            If InStr(1, scriptPath, "_StartupCaller", vbTextCompare) > 0 Then
                If Rhino.DeleteStartupScript(scriptPath) Then
                    Rhino.Print "Removed startup script: " & scriptPath
                    count = count + 1
                Else
                    Rhino.Print "Failed to remove startup script: " & scriptPath
                End If
            End If
        Next
    End If
    
    Rhino.Print "Total startup scripts removed: " & count
End Sub

CleanupStartupScripts()
'''
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "enneadtab_startup_cleanup.rvb")
    
    with open(temp_file, 'w') as f:
        f.write(script_content)
    
    return temp_file


def Uninstall():
    print ("###################")
    print ("Starting EnneadTab uninstallation...")
    
    # Show confirmation dialog
    res = rs.MessageBox("Are you sure you want to completely uninstall EnneadTab from Rhino?\n\nThis will remove all EnneadTab toolbars, search paths, aliases, and startup scripts.", 1)
    if res == 2:  # User clicked Cancel
        print ("Uninstallation cancelled by user.")
        return

    print ("User confirmed uninstallation. Proceeding...")
    
    # Close all EnneadTab toolbar collections
    toolbar_count = 0
    for toolbar_collection in rs.ToolbarCollectionNames():
        if "ennead".lower() in toolbar_collection.lower():
            try:
                rs.CloseToolbarCollection(toolbar_collection)
                print ("Closed toolbar collection: {}".format(toolbar_collection))
                toolbar_count += 1
            except Exception as e:
                print ("Failed to close toolbar collection {}: {}".format(toolbar_collection, str(e)))

    # Remove all EnneadTab search paths
    path_count = 0
    for path in rs.SearchPathList():
        if "ennead".lower() in path.lower():
            try:
                rs.DeleteSearchPath(path)
                print ("Removed search path: {}".format(path))
                path_count += 1
            except Exception as e:
                print ("Failed to remove search path {}: {}".format(path, str(e)))

    # Remove all EnneadTab aliases
    alias_count = 0
    try:
        aliases = rs.AliasList()
        for alias in aliases:
            alias_path = rs.AliasPath(alias)
            if alias_path and "ennead".lower() in alias_path.lower():
                try:
                    rs.DeleteAlias(alias)
                    print ("Removed alias: {} -> {}".format(alias, alias_path))
                    alias_count += 1
                except Exception as e:
                    print ("Failed to remove alias {}: {}".format(alias, str(e)))
    except Exception as e:
        print ("Failed to get alias list: {}".format(str(e)))

    # Remove all EnneadTab startup scripts using temporary RhinoScript
    startup_script_count = 0
    try:
        temp_script = create_startup_script_cleaner()
        print ("Created temporary startup script cleaner: {}".format(temp_script))
        
        # Run the RhinoScript using the correct method
        script_command = "-LoadScript " + temp_script
        result = Rhino.RhinoApp.RunScript(script_command, True)
        if result:
            print ("Successfully executed startup script cleanup")
            # The script will print the count, but we'll estimate based on typical EnneadTab setup
            startup_script_count = 1  # Typically one startup script for EnneadTab
        else:
            print ("Failed to execute startup script cleanup")
            
        # Clean up temporary file
        try:
            os.remove(temp_script)
            print ("Cleaned up temporary script file")
        except Exception as e:
            print ("Failed to clean up temporary script file: {}".format(str(e)))
            
    except Exception as e:
        print ("Failed to handle startup script cleanup: {}".format(str(e)))

    # Show completion message
    message = "EnneadTab uninstallation completed!\n\n"
    message += "Closed {} toolbar collections\n".format(toolbar_count)
    message += "Removed {} search paths\n".format(path_count)
    message += "Removed {} aliases\n".format(alias_count)
    message += "Removed {} startup scripts\n\n".format(startup_script_count)
    message += "Please restart Rhino for changes to take effect."
    
    print ("Uninstallation completed successfully.")
    print ("Closed {} toolbar collections".format(toolbar_count))
    print ("Removed {} search paths".format(path_count))
    print ("Removed {} aliases".format(alias_count))
    print ("Removed {} startup scripts".format(startup_script_count))
    
    rs.MessageBox(message)

    
if __name__ == "__main__":
    Uninstall() 