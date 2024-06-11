__doc__ = "XXXshould make into a smart button so that it toggle between clear and create"
__title__ = "Visulaize\nShaft"



"""
checkcurrent view is  3d view



can turn on temp view template to half tone every thing elese and




need another toll to clear out all visualised void with comment 'xxxxxxx'
"""

from pyrevit import DB, revit, script, forms
import System


def clear_existing_solid_shaft():

    all_generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    for item in all_generic_models:
        if item.LookupParameter("Comments").AsString() == global_comment:
            revit.doc.Delete(item.Id)


def find_c(category_name):
    for category in revit.doc.Settings.Categories:
        if category.Name == category_name:
            return category

def sort_crv(crvs):#work only with single loop-like, if double loop then it ewill fail
    current_crv = crvs[0]
    end_pt = current_crv.GetEndPoint(1)
    sorted_crv = [current_crv]
    i = 0#safety count
    while len(sorted_crv) < len(crvs):
    #for i, crv in enumerate(crvs):

        for other_crv in crvs:
            if current_crv == other_crv:#skip itself
                #print "self"
                continue
            elif end_pt.IsAlmostEqualTo( other_crv.GetEndPoint(0) ):#this is the next curve
                #print "found"
                sorted_crv.append(other_crv)
                current_crv = other_crv
                end_pt = current_crv.GetEndPoint(1)
                #print sorted_crv
                break
            else:#not the next crv
                #print "not this one"
                pass

        i += 1
        if i > 500:
            break
    return sorted_crv

def make_solid_from_shaft_alt(shaft):
    opt = DB.Options()
    opt.IncludeNonVisibleObjects = True
    geo = shaft.Geometry(opt)
    #print geo

    DS_obj = DB.DirectShape.CreateElement(revit.doc, find_c("Generic Models").Id)
    DS_obj.SetShape([geo])
    DS_obj.LookupParameter("Comments").Set(global_comment)
    return DS_obj



def make_solid_from_shaft(shaft):
    #create DB.Solid with the shaft geomtry, assign to special equipment category
    """
    geo = shaft.Geometry[DB.Options()]
    print(geo)
    print(list(geo))
    print(shaft.get_Geometry(DB.Options()))
    DS_obj = DB.DirectShape.CreateElement(revit.doc, find_c("Generic Models").Id)
    print(DS_obj.SetShape(geo))
    #print DS_obj.SetShape(list(geo))
    """
    if shaft.IsRectBoundary:
        boundary = shaft.BoundaryRect
    else:
        boundary = shaft.BoundaryCurves


    #print boundary
    #print len(list(boundary))
    #print list(boundary)



    crv_loop = DB.CurveLoop()#initiate emoty crv loop obj
    for line in sort_crv(list(boundary)):
        #print "~~~~~~~~~~"
        #print line
        try:
            crv_loop.Append(line)
        except Exception as e:
            #print (e)
            #print "will try reverse this line"
            temp_line = DB.Curve.CreateReversed(line)
            #print temp_line
            try:
                crv_loop.Append(temp_line)
            except:
                #print "do this line later, move it back in boundary."
                continue
    #print crv_loop
    #print DB.XYZ.BasisZ
    #print list(crv_loop)
    #print len(list(crv_loop))
    sketch = System.Collections.Generic.List[DB.CurveLoop]([DB.CurveLoop.Create(list(crv_loop))])
    #print sketch

    h = shaft.LookupParameter("Unconnected Height").AsDouble()

    geo = DB.GeometryCreationUtilities.CreateExtrusionGeometry(sketch, DB.XYZ.BasisZ, h)
    #print geo
    DS_obj = DB.DirectShape.CreateElement(revit.doc, find_c("Generic Models").Id)
    DS_obj.SetShape([geo])


    DS_obj.LookupParameter("Comments").Set(global_comment)
    return DS_obj
    """

    doc.Paint() get all face of the solid a bring pink material
    if no pink material valible, create one with name "$$QAQC material"
    """



    #cannot use ,geomtry peoperty becasue there is nothing to show thus nothing to extract
    #....so i have to turn to extract the sketch line fitst, then use the unconnected height to create solid



    #make the comment = "EA_VisualisedShaft Tool"
    #randomize the display color as Override


def process_shaft_data(shaft):
    print("~~~~~~\n#####new shaft")
    #shape = make_solid_from_shaft(shaft)
    try:
        shape = make_solid_from_shaft(shaft)
    except Exception as e:
        print("####################")
        print (e)
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("bad shaft:" + str(shaft.Id))
        print("maybe more than one close loop in sketch, this should be fixed as single boundary shaft.")
        shape = None
    #return shaft para infor

    #return the element that is being cut by this shaft
    #ElementIntersectsSolidFilter class
    #find all floor slabs that can intersect with this shaft solid.


    data = []

    for para in shaft.Parameters:
        #print "{} = {}".format(para.Definition.Name, para.AsValueString() )
        data.append("{} = {}".format(para.Definition.Name, para.AsValueString() ))


    """
    print("###")
    print(shaft.GetParameters("Base Constraint")[0].AsValueString())
    """

    return data, shape



########## main code below ##########


#check if current view is 3d
if isinstance(revit.active_view, DB.View3D) == False:
    forms.alert("You must be on a 3D view for this tool to work.")
    script.exit()


#check if temp view template is on, and alert user that temp view template will activate to highlight the solid nShaft



#get all shaft element
all_shafts = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_ShaftOpening).WhereElementIsNotElementType().ToElements()


#for each shaft, progress shaft  function(shaft), return data
data = []
shapes = []
with revit.Transaction("Visualize Shaft"):
    #clear cur3ent visulised shaft with comment "$$EnneadTab_VisualisedShaft Tool"
    global_comment = "$$EnneadTab_VisualisedShaft Tool"
    clear_existing_solid_shaft()


    for shaft in all_shafts:
        data.append(  process_shaft_data(shaft)[0]  )
        shapes.append(   process_shaft_data(shaft)[1]  )


new_shapes = []
for shape in shapes:
    if shape == None:
        continue
    new_shapes.append(shape)


with revit.Transaction("Isolate Shaft Shapes"):
    #revit.active_view.EnableTemporaryViewMode()
    shape_collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in new_shapes])
    revit.active_view.IsolateElementsTemporary(shape_collection)
    pass


#print in table
