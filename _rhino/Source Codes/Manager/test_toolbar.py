import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    toolbar_details = ""
    names = rs.ToolbarCollectionNames()
    if names:
        for name in names:
            toolbar_details += "\t\t\t\t{}:   {}\n".format(name, rs.ToolbarCollectionPath(name))
            toolbars = rs.ToolbarNames(name)
            toolbar_groups = rs.ToolbarNames(name, groups = True)
            if toolbars:
                for toolbar in toolbars:
                    
                    if toolbar == "Ennead_20220509":
                        print(rs.HideToolbar("default", toolbar))
                        """
                        for toolbar_group in toolbar_groups:
                            try:
                                print(rs.HideToolbar(toolbar, toolbar_group))
                            except Exception as e:
                                print(e)
                        """        
                                
                        
            if toolbar_groups:
                for toolbar_group in toolbar_groups:
                    if "Ennead_" in toolbar_group:
                        print(rs.HideToolbar("default", toolbar_group))
                    toolbar_details += "\t\t\t\t\t\t-Toolbar Group:  {}\n".format(toolbar_group)

            toolbar_details += "\n\n"


    rs.TextOut(message = "Current Toolbar Collection\n{}".format(toolbar_details))
    
    
###############################
if __name__ == "__main__":
    main()