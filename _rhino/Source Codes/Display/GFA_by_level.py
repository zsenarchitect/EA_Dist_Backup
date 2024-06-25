from EnneadTab import NOTIFICATION
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import clr # pyright: ignore
import System # pyright: ignore

import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)




import System # pyright: ignore
import Rhino # pyright: ignore.UI
import Eto # pyright: ignore

FORM_KEY = 'GFA_BY_LEVEL_modeless_form'

"""
import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations
"""

class DataItem():
    def __init__(self, item, row, column):
        self.item = item
        self.row = row
        self.column = column


# make modal dialog
class GfaByLevelDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "GFA By Level Exporter"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 400
        self.width = 400
        self.selected_polysurf = None
        self.data = None

        self.Closed += self.OnFormClosed




        # initialize layout
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.Padding = Eto.Drawing.Padding(5)
        main_layout.Spacing = Eto.Drawing.Size(5, 5)



        # add listBox
        main_layout.BeginVertical()
        main_layout.AddRow(self.CreatePicker())
        main_layout.AddRow(self.CreateLevelDataInput())
        main_layout.EndVertical()





        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        # add message
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.AddRow(self.CreateExpander())
        layout.EndVertical()


        layout.BeginVertical()
        layout.AddRow(main_layout)
        layout.EndVertical()

        # add buttons
        layout.BeginVertical()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        # set content
        self.Content = layout
        self.InitiateFiller()
        
        EnneadTab.RHINO.RHINO_UI.apply_dark_style(self)

    @property
    def main_brep(self):
        if self.selected_polysurf:
            return rs.coercebrep(self.selected_polysurf)
        return None

    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Pick an envolope massing and preview its floor GFA by levels."
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left


    def CreateExpander(self):
        self.expander = Eto.Forms.Expander ()
        self.expander.Header = "Quick Help"
        self.expander.Expanded = False
        msg = Eto.Forms.Label()
        msg.Text = "helper document to be filled in....."
        self.expander.Content = msg
        return self.expander



    def CreatePicker(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        pick_bn = Eto.Forms.Button(Text = 'Pick Input Polysurf')
        pick_bn.Click += self.btn_Pick_Clicked

        self.brep_label = Eto.Forms.Label(Text = '')
        layout.AddRow(pick_bn,  self.brep_label)

        return layout

    def CreateLevelDataInput(self):


        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)


        B = Eto.Forms.Label(Text = 'Number of Level')
        C = Eto.Forms.Label(Text = 'FTF')
        layout.AddRow(None, B, C)

        A = Eto.Forms.Label(Text = 'Top Zone')
        self.tbox_top_num = Eto.Forms.TextBox()
        self.tbox_top_FTF = Eto.Forms.TextBox()
        layout.AddRow(A, self.tbox_top_num, self.tbox_top_FTF)

        A = Eto.Forms.Label(Text = 'Mid Zooe')
        self.tbox_mid_num = Eto.Forms.TextBox()
        self.tbox_mid_FTF = Eto.Forms.TextBox()
        layout.AddRow(A, self.tbox_mid_num, self.tbox_mid_FTF)

        A = Eto.Forms.Label(Text = 'Bm Zone')
        self.tbox_bm_num = Eto.Forms.TextBox()
        self.tbox_bm_FTF = Eto.Forms.TextBox()
        layout.AddRow(A, self.tbox_bm_num, self.tbox_bm_FTF)

        self.sum_label = Eto.Forms.Label(Text = '')
        layout.AddRow(None, None, self.sum_label)


        return layout


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def InitiateFiller(self):

        self.filler_list = ["tbox_top_num","tbox_mid_num","tbox_bm_num","tbox_top_FTF","tbox_mid_FTF", "tbox_bm_FTF"]
        for x in self.filler_list:
            if "num" in x:
                default = 1
            else:
                default = 3
            value = EnneadTab.DATA_FILE.get_sticky_longterm(x, default_value_if_no_sticky = default)

            #setattr(self, x , str(value))
            tbox = getattr(self, x)
            tbox.Text  = str(value)







    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Preview result"
        self.btn_Run.Click += self.btn_preview_Clicked
        user_buttons.append(self.btn_Run)

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Export data to Excel"
        self.btn_Run.Click += self.btn_export_Clicked
        user_buttons.append(self.btn_Run)


        user_buttons.append(None)
        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Process"
        self.btn_Run.Click += self.btn_process_Clicked
        user_buttons.append(self.btn_Run)

        """
        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked


        user_buttons.extend([ None, self.btn_Cancel])
        """
        return user_buttons


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_export_Clicked(self, sender, e):
        if not self.data:
            return
        data_collection = []
        max = len(self.data.keys())
        for i, value in self.data.items():
            level, area = "Level {}".format(i + 1), value

            area = convert_area_to_good_unit(area)
            #print area
            area_num, area_unit = area.split(" ", maxsplit = 1)
            #print area_num

            row = max - i - 1
            cell_level = DataItem(level, row, 0)
            cell_area = DataItem(float(area_num), row, 1)
            cell_unit = DataItem(area_unit, row, 2)
            data_collection.append(cell_level)
            data_collection.append(cell_area)
            data_collection.append(cell_unit)

        #data_collection.reverse()
        bake_action(data_collection)

    # event handler handling clicking on the 'run' button
    def btn_preview_Clicked(self, sender, e):
        self.generate_level_crvs(is_preview = True)

    def btn_process_Clicked(self, sender, e):
        self.generate_level_crvs(is_preview = False)

    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close()

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def btn_Pick_Clicked(self, sender, e):
        select_obj = rs.GetObject(message = "Pick enclused polysurface as one massing", filter = 16, select = True)
        if select_obj:
            self.brep_label.Text = "Polysurface captured!"

            self.selected_polysurf = select_obj
        else:
            self.brep_label.Text = "Polysurface not defined!"

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def Close(self):
        # Remove the events added in the initializer
        #self.RemoveEvents()
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key(FORM_KEY):
            form = sc.sticky[FORM_KEY]
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove(FORM_KEY)

        for x in self.filler_list:
            if not hasattr(self, x):
                continue
            tbox = getattr(self, x)
            EnneadTab.DATA_FILE.set_sticky_longterm(x, tbox.Text)



    @EnneadTab.ERROR_HANDLE.try_catch_error
    def generate_level_crvs(self, is_preview):


        try:
            self.top_num = int(self.tbox_top_num.Text)
            self.mid_num = int(self.tbox_mid_num.Text)
            self.bm_num = int(self.tbox_bm_num.Text)
            self.top_FTF = float(self.tbox_top_FTF.Text)
            self.mid_FTF = float(self.tbox_mid_FTF.Text)
            self.bm_FTF = float(self.tbox_bm_FTF.Text)
        except:
            print("data not valid")
            return



        if not self.selected_polysurf:
            print("brep not valid")
            return


        #print self.main_brep


        rs.UnselectAllObjects()
        rs.EnableRedraw(False)
        #print self.top_num
        #print self.mid_num
        #print self.bm_num
        #print self.top_FTF
        #print self.mid_FTF
        #print self.bm_FTF
        #print "run"

        #print self.selected_polysurf
        #print rs.BoundingBox(self.selected_polysurf)
        #print rs.BoundingBox(self.selected_polysurf)[0]
        plane_z = rs.BoundingBox(self.selected_polysurf)[0][2]
        FTF_list = [self.bm_FTF] * self.bm_num + [self.mid_FTF] * self.mid_num + [self.top_FTF] * self.top_num
        #print FTF_list


        # need to remove preview crvs no matter what
        obj_name = "EA_GFA_LEVEL_CRVS_PREVIEW"
        old_crvs = rs.ObjectsByName(obj_name)
        rs.DeleteObjects(old_crvs)

        if not is_preview:
            obj_name = "EA_GFA_LEVEL_CRVS"


        self.plane_crvs = []
        self.dots = []
        self.data = dict()
        for i in range(self.top_num + self.mid_num + self.bm_num):
            plane = rs.PlaneFromNormal([0,0,plane_z], [0,0,1])
            #pts = clr.StrongBox[System.Array[Rhino.Geometry.Point3d]](Rhino.Geometry.Point3d(0,0,0))
            #crvs = clr.StrongBox[System.Array[Rhino.Geometry.Curve]](Rhino.Geometry.PolyCurve ())
            pts = clr.StrongBox[System.Array[Rhino.Geometry.Point3d]]()
            crvs = clr.StrongBox[System.Array[Rhino.Geometry.Curve]]()
            Rhino.Geometry.Intersect.Intersection.BrepPlane(self.main_brep, plane, sc.doc.ModelAbsoluteTolerance, crvs, pts)

            """
            print("###")
            if not crvs.Value:
                continue
            print(crvs)
            print(list(crvs.Value))
            """
            """
            for x in dir(crvs):
                print(x)
            print(crvs[0])
            print(list(crvs))
            """
            #print crvs.tolist()
            if not crvs.Value:
                continue
            crvs = list(crvs.Value)
            crvs = Rhino.Geometry.Curve.JoinCurves(crvs)
            #crvs = list(crvs.Value)

            self.data[i] = 0
            for crv in crvs:

                doc_crv = sc.doc.Objects.AddCurve(crv.ToNurbsCurve() )
                self.plane_crvs.append(doc_crv)
                try:
                    area = rs.Area(doc_crv)
                    text = convert_area_to_good_unit(area)
                    self.data[i] += area

                except:
                    text = "Cannot get area"
                dot = rs.AddTextDot(text, EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(doc_crv))
                self.dots.append(dot)

            plane_z += FTF_list[i]

        rs.ObjectName(self.plane_crvs, name = obj_name)
        rs.ObjectName(self.dots, name = obj_name)
        rs.AddObjectsToGroup(self.plane_crvs, rs.AddGroup())
        rs.AddObjectsToGroup(self.dots, rs.AddGroup())




        rs.Redraw()
        rs.EnableRedraw(True)

        total_area = 0
        for i, value in self.data.items():
            total_area += value
        total_area = convert_area_to_good_unit(total_area)
        self.sum_label.Text = "Sum = {}".format(total_area)





    def OnFormClosed(self, sender, e):
        self.Close()

def convert_area_to_good_unit(area):
    # only provide sqm or sqft, depeding on which system it is using. mm and m -->sqm, in, ft -->sqft

    unit = rs.UnitSystemName(capitalize=False, singular=True, abbreviate=False, model_units=True)

    def get_factor(unit):
        if unit == "millimeter":
            return 1.0/(1000 * 1000), "SQM"
        if unit == "meter":
            return 1.0, "SQM"
        if unit == "inch":
            return 1.0/(12 * 12), "SQFT"
        if unit == "foot":
            return 1.0, "SQFT"
        return -1, "{0} x {0}".format(unit)
    factor, unit_text = get_factor(unit)
    if factor < 0:
        return "{:.2f} {}".format(area, unit_text)


    area *= factor
    return "{:.2f} {}".format(area, unit_text)
    pass

def bake_action(data):
    filename = "EnneadTab GFA Schedule"
    if sc.doc.Name is not None:
        filename = "{}_EnneadTab GFA Schedule".format(sc.doc.Name.replace(".3dm", ""))


    filepath = rs.SaveFileName(title = "Where to save the Excel?", filter = "Excel Files (*.xlsx)|*.xlsx||", filename = filename)
    if filepath is None:
        return
    EnneadTab.EXCEL.save_data_to_excel(data, filepath, worksheet = "EnneadTab GFA")


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    NOTIFICATION.messenger("are you sure???")
    return
    rs.EnableRedraw(False)
    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = GfaByLevelDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg
    return
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
    if (rc):

        datas = dlg.main()

        return

    else:
        print("Dialog did not run")
        return



######################  main code below   #########
if __name__ == "__main__":

    main()
