import ENVIRONMENT
import FOLDER
import os
import time
import random

if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import rhinoscriptsyntax as rs
    import Rhino # pyright: ignore


def update_rui_v7():
    

    for tool_bar_name in rs.ToolbarCollectionNames():
        if ENVIRONMENT.PLUGIN_NAME.lower() in tool_bar_name.lower():
            rs.CloseToolbarCollection(tool_bar_name, prompt=False)


    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.DIST_RUI_CLASSIC)
    rs.OpenToolbarCollection(my_local_version)

def update_rui_v8():
    # todo: figure out a way to deal with R8 rui handle disapear after restart
    good_rui_toolbar_name = os.path.basename(ENVIRONMENT.DIST_RUI_MODERN).replace(".rui", "")

    for tool_bar_name in rs.ToolbarCollectionNames():
        # do not close current oppedn mordern rui so it will not deacivate and disappear after restart
        if good_rui_toolbar_name == tool_bar_name:
            continue

        if ENVIRONMENT.PLUGIN_NAME.lower() in tool_bar_name.lower():
            rs.CloseToolbarCollection(tool_bar_name, prompt=False)


    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.DIST_RUI_MODERN)
    rs.OpenToolbarCollection(my_local_version)




def update_my_rui():
    if rs.ExeVersion() >= 8:
        update_rui_v8()
    else:
        update_rui_v7()


    



def add_startup_script():
    
    """hear me out here:
    python cannot add startup script directly
   
    i use this python script C to call rhino script B to call rhino script A, which is the command alias
    This will not run the startup command, it just add to the start sequence.
    """
    max_attempts = 3
    
    rvb_caller_script_path = "{}\\{}_StartupCaller.rvb".format(ENVIRONMENT.WINDOW_TEMP_FOLDER, ENVIRONMENT.PLUGIN_NAME)

    rvb_caller_content = """
Option Explicit

Sub StartupCaller()
    Dim commandName
    commandName = "{}_{}_Startup"
    Call Rhino.Command(commandName)
End Sub

Call StartupCaller()
""".format(ENVIRONMENT.PLUGIN_ABBR, ENVIRONMENT.PLUGIN_NAME)

    # Use retry logic for the first file
    for attempt in range(max_attempts):
        try:
            with open(rvb_caller_script_path, "w") as f:
                f.write(rvb_caller_content)
            break
        except IOError as e:
            if attempt < max_attempts - 1:
                # Add a small random delay to avoid race conditions
                time.sleep(0.5 + random.random())
                continue
            else:
                print("Failed to write caller script after {} attempts: {}".format(max_attempts, e))
                raise

    rvb_startup_modifier_script_path = "{}\\{}_StartupEnable.rvb".format(ENVIRONMENT.WINDOW_TEMP_FOLDER, ENVIRONMENT.PLUGIN_NAME)

    rvb_startup_modifier_content = """
Option Explicit

Sub StartupEnable()
    On Error Resume Next
    
    Dim filePath
    Dim intCount
    Dim arrPaths
    Dim strPath
    Dim temp_folder
    
    temp_folder = "C:\\temp\\{}_Dump"

    ' Get count of startup scripts
    intCount = Rhino.StartupScriptCount
    
    ' If there are scripts, check for ones containing "menu" and remove them
    If intCount > 0 Then
        arrPaths = Rhino.StartupScriptList
        For Each strPath in arrPaths
            If InStr(strPath, "menu") > 0 Then
                Call Rhino.DeleteStartupScript (strPath)
            End If
        Next
    End If
    
    filePath = temp_folder & "\\{}_StartupCaller.rvb"
    
    ' Ensure path with spaces is handled correctly by enclosing in quotes
    filePath = Chr(34) & filePath & Chr(34)
    
    Call Rhino.AddStartupScript(filePath)
    
    If Err.Number <> 0 Then
        Call Rhino.Print("Error in StartupEnable: " & Err.Description)
    End If
End Sub

Call StartupEnable()
""".format(ENVIRONMENT.PLUGIN_NAME, ENVIRONMENT.PLUGIN_NAME)

    # Use retry logic for the second file
    for attempt in range(max_attempts):
        try:
            with open(rvb_startup_modifier_script_path, "w") as f:
                f.write(rvb_startup_modifier_content)
            break
        except IOError as e:
            if attempt < max_attempts - 1:
                # Add a small random delay to avoid race conditions
                time.sleep(0.5 + random.random())
                continue
            else:
                print("Failed to write startup modifier script after {} attempts: {}".format(max_attempts, e))
                raise
                
    Rhino.RhinoApp.RunScript("-LoadScript " + rvb_startup_modifier_script_path, True)
    
def unit_test():
    pass

    
if __name__ == "__main__":

    update_my_rui()