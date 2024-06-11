__doc__ = "Worth revisiting idea. This find the ending curtain panel in curtain wall."
__title__ = "find terminal panel"

from pyrevit import forms, DB, revit, script

def set_panel_info(panel, info):
    panel.LookupParameter("Comments").Set(info)

def set_panel():
    selection = revit.get_selection()

    walls = filter(lambda x: x.Category.Name == "Walls", selection)
    for wall in walls:
        grids = wall.CurtainGrid
        #print grids
        #print grids.GetVGridLineIds()
        """
        for Vgrid in grids.GetVGridLineIds():
            print(revit.doc.GetElement(Vgrid).FullCurve.GetEndPoint(0))
        """

        panel_collection = [ revit.doc.GetElement(x) for x in wall.CurtainGrid.GetPandelIds()]

        print(panel_collection)
        for panel in panel_collection:
            x = 0


        panels = []
        x = 0
        y = 0
        for U in grids.GetUGridLineIds():
            x += 1
            for V in grids.GetVGridLineIds():
                y += 1
                panel = grids.GetPanel(U, V)
                panels.append( panel)
                set_panel_info(panel, str(x) + "+" + str(y))
        #panel_starting = [grids.GetPanel(list(grids.GetVGridLineIds())[0],x) for x in grids.GetUGridLineIds()]
        #panel_ending = [grids.GetPanel(list(grids.GetVGridLineIds())[-1],x) for x in grids.GetUGridLineIds()]
        """
        for panel in panels:
            set_panel_info(panel, "start")
            """
        """
        for row in panels_by_row:
            for panel in row:
                set_panel_info(panel, "start")
        """
            #set_panel_info(row[0], "start")
            #set_panel_info(row[-1], "end")


################## main code below #####################
output = script.get_output()
output.close_others()


with revit.Transaction("set ending panel info"):
    set_panel()
