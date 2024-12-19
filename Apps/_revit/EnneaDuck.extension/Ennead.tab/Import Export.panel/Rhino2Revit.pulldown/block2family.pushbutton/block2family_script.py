#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "After getting all the block data from Rhino side, create/update family in Revit. If the edit is about moving/rotating in rhino, the revit side will remove old family instance and get a new one based on saved Rhino Id."
__title__ = "Block2Family"
__tip__ = True

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()


import os
import math
import clr # pyright: ignore 
# from pyrevit import forms #
from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms #

from EnneadTab import ERROR_HANDLE, FOLDER, DATA_FILE, NOTIFICATION, LOG, ENVIRONMENT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_UNIT
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import ApplicationServices # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()

KEY_PREFIX = "BLOCKS2FAMILY"

def get_block_name_from_data_file(data_file):
    return data_file.replace(".sexyDuck", "").replace(KEY_PREFIX + "_", "")

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def block2family():
    for _doc in REVIT_APPLICATION.get_app().Documents:
        if _doc.IsFamilyDocument:
            try:
                _doc.Close()
            except:
                pass

    data_files = [file for file in os.listdir(FOLDER.DUMP_FOLDER) if file.startswith(KEY_PREFIX) and file.endswith(".sexyDuck")]

    face_model_selection = forms.SelectFromList.show([get_block_name_from_data_file(x) for x in sorted(data_files)],
                                                     multiselect = True,
                                                     width = 1000,
                                                     button_name = "Use UV projection for selected blocks",
                                                     title="How was your block orgin defined? If it was laid on XY then it is UV projection, if it was standing then it is NOT UV projection.")
    
    if face_model_selection is None:
        return
    
    for i, data_file in enumerate(data_files):
        block_name = get_block_name_from_data_file(data_file)
        NOTIFICATION.messenger("Loading {}/{}...{}".format(i+1, len(data_files),block_name))
        process_file(data_file, block_name in face_model_selection)
           
    NOTIFICATION.messenger("All Rhino blocks have been loaded to Revit! Hooray!!")




def process_file(data_file, use_UV_projection):
    load_family(data_file)
    update_instances(data_file, use_UV_projection)




def load_family(file):
    data = DATA_FILE.get_data(file)

    geo_data = data["geo_data"]
    para_names = []
    for id, info in geo_data.items():
        user_data = info["user_data"]
        para_names.extend(user_data.keys())

    para_names = list(set(para_names))
    
    unit = data["unit"] # ft, in, m, mm
    if unit in ["ft", "in"]:
        template_unit = "ft"
    elif unit in ["m", "mm"]:
        template_unit = "mm"
    else:
        NOTIFICATION.messenger("Wait, cannot use this unit [{}]".format(unit))
        return
    template = "{}\\BaseFamily_{}.rft".format(os.path.dirname(__file__), template_unit)

    # create new family from path(loaded with shared parameter), 
    family_doc = ApplicationServices.Application.NewFamilyDocument (REVIT_APPLICATION.get_app(), template)

    block_name = get_block_name_from_data_file(file)
    geo_folder = FOLDER.get_EA_dump_folder_file(KEY_PREFIX + "_" + block_name)
    t = DB.Transaction(family_doc, __title__)
    t.Start()
    for file in os.listdir(geo_folder):
        geo_file = os.path.join(geo_folder, file)
        if ".dwg" in geo_file:
            DWG_convert(family_doc, geo_file)
            
        # get in geos, 
        #free_form_convert(family_doc, geo_file)

    manager = family_doc.FamilyManager
    existing_para_names = [x.Definition.Name for x in manager.GetParameters()]
    for para_name in para_names:
        if para_name in existing_para_names:
            continue
        
        manager.AddParameter(para_name, DB.GroupTypeId.Data, REVIT_UNIT.lookup_unit_spec_id("text"), True)
         
    t.Commit()

    # load to project
    option = DB.SaveAsOptions()
    option.OverwriteExistingFile = True
    family_container_folder = ENVIRONMENT.ONE_DRIVE_DESKTOP_FOLDER + "\\EnneadTab Temp Family Folder"
    if not os.path.exists(family_container_folder):
        os.mkdir(family_container_folder)
    family_doc.SaveAs(family_container_folder + "\\" + block_name + ".rfa",
                      option)

    REVIT_FAMILY.load_family(family_doc, doc)

    
def DWG_convert(doc, geo_file):

    exisiting_cads = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements()
    exisiting_import_OSTs = get_current_import_object_styles(doc)

    options = DB.DWGImportOptions()
    cad_import_id = clr.StrongBox[DB.ElementId]()
    with ErrorSwallower() as swallower:
        doc.Import(geo_file, options,
                    doc.ActiveView, cad_import_id)

    current_cad_imports = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).ToElements()
    for cad_import in current_cad_imports:
        if cad_import not in exisiting_cads:
            break

    # in rare condition there is no cad import at this step, need investigation..
    if not cad_import:
        print("No CAD import found in the family document.")
        return

    cad_trans = cad_import.GetTransform()
    cad_type = cad_import.Document.GetElement(cad_import.GetTypeId())


    family_cat = doc.OwnerFamily.FamilyCategory

    geo_elem = cad_import.get_Geometry(DB.Options())
    geo_elements = []
    for geo in geo_elem:
        if isinstance(geo, DB.GeometryInstance):
            geo_elements.extend([x for x in geo.GetSymbolGeometry()])

    solids = []

    layer_name = FOLDER.get_file_name_from_path(geo_file, include_extension=False)
    for gel in geo_elements:

        if isinstance(gel, DB.Solid):
            solids.append(gel)



    # create freeform from solids
    converted_els = []
    # Convert CAD Import to FreeFrom/DirectShape"
    for solid in solids:
        converted_els.append(DB.FreeFormElement.Create(doc, solid))

    cad_import.Pinned = False
    doc.Delete(cad_import.Id)


    assign_subC(converted_els, subC=get_subC_by_name(doc,layer_name))

    try:
        clean_import_object_style(doc, existing_OSTs=exisiting_import_OSTs)
    except Exception as e:
        print("fail to clean up imported category SubC becasue " + str(e))

def clean_import_object_style(doc, existing_OSTs):
    import_OSTs = get_current_import_object_styles(doc)

    for import_OST in import_OSTs:
        if import_OST not in existing_OSTs:
            # print "--deleting imported DWG SubC: " + import_OST.Name
            doc.Delete(import_OST.Id)
    # print "\n\nCleaning finish."
        
def get_current_import_object_styles(doc):
    categories = doc.Settings.Categories
    import_OSTs = filter(lambda x: "Imports in Families" in x.Name, categories)
    if len(import_OSTs) == 0:
        return
    import_OSTs = list(import_OSTs[0].SubCategories)
    return import_OSTs
        


        
def free_form_convert( doc, geo_file):

    layer_name = FOLDER.get_file_name_from_path(geo_file, include_extension=False)

    converted_els = []
    geos = DB.ShapeImporter().Convert(doc, geo_file)
    for geo in geos:
        try:
            converted_els.append(DB.FreeFormElement.Create(doc, geo))
        except Exception as e:
            print("-----Cannot import this part of file, skipping: {}".format(geo))
            print(e)

    assign_subC(converted_els, subC=get_subC_by_name(doc, layer_name))

        
def assign_subC(converted_els, subC):
    for element in converted_els:
        element.Subcategory = subC

def get_subC_by_name(doc, name):
    parent_category = doc.OwnerFamily.FamilyCategory
    subCs = parent_category.SubCategories
    for subC in subCs:
        if subC.Name == name:
            return subC
    parent_category = doc.OwnerFamily.FamilyCategory
    new_subc = doc.Settings.Categories.NewSubcategory(parent_category, name)
    return new_subc



def update_instances(file, use_UV_projection):
    t = DB.Transaction(doc, __title__)
    t.Start()
    block_name = get_block_name_from_data_file(file)
    exisitng_instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(family_name=block_name, type_name=block_name, doc=doc)
    exisitng_instances_map = {x.LookupParameter("Rhino_Id").AsString(): x for x in exisitng_instances}
    
    data = DATA_FILE.get_data(file)
    unit = data["unit"]
    if unit == "ft":
        factor = 1
    elif unit == "in":
        factor = 1/12
    elif unit == "mm":
        factor = REVIT_UNIT.mm_to_internal(1)
    else:
        factor = REVIT_UNIT.m_to_internal(1)

        
    geo_data = data["geo_data"]

    type = REVIT_FAMILY.get_family_type_by_name(family_name=block_name, type_name=block_name, doc=doc)
    type.LookupParameter("Description").Set("EnneadTab Block Convert")

    for id, info in geo_data.items():
        if id in exisitng_instances_map:
            instance = exisitng_instances_map[id]
            doc.Delete(instance.Id)
        transform_data = info["transform_data"]
        instance = place_new_instance(type, transform_data, factor, use_UV_projection)
        user_data = info["user_data"]
        for key, value in user_data.items():
            if instance.LookupParameter(key) is None:
                continue

            if key == "Projected_Area":
                value = factor * float(value)
            if key in ["Panel_Width", "Panel_Height"]:
                value = factor * float(value)
            instance.LookupParameter(key).Set(value)
            
        instance.LookupParameter("Rhino_Id").Set(id)
    t.Commit()

        
def place_new_instance(type, transform_data, factor, use_UV_projection):
    """_summary_

    Args:
        type (_type_): _description_
        transform_data (_type_): _description_
        factor (_type_): _description_
        use_UV_projection (Bool): True if you are modeling the facade laying flat, aka UV = XY,
        False if it is modelied standing, aka XY = XY

    Returns:
        _type_: _description_
    """
    
    transform = transform_data['transform']
    rotation_tuple = transform_data["rotation"]
    reflection = transform_data["is_reflection"]
    X = transform[0][-1] * factor
    Y = transform[1][-1] * factor
    Z = transform[2][-1] * factor

    temp_instance = DB.AdaptiveComponentInstanceUtils.CreateAdaptiveComponentInstance(doc, type)
    insert_pt = DB.AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(temp_instance)[0]
    # print(doc.GetElement(insert_pt).Position.Z)
    # DB.AdaptiveComponentInstanceUtils.MoveAdaptiveComponentInstance (temp_instance , DB.Transform.CreateTranslation(DB.XYZ(0,0,-doc.GetElement(insert_pt).Position.Z)), True)
    # print(doc.GetElement(insert_pt).Position.Z)

    rotation = DB.Transform.CreateTranslation(DB.XYZ(0,0,0))# this is a empty move, just to create a transofmrm

    rotate_angle_x, rotate_angle_y, rotate_angle_z = rotation_tuple
   

    axis = DB.XYZ(0,0,1)
    axis = rotation.BasisZ
    angle = rotate_angle_z
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation
    if reflection and not use_UV_projection:
        DB.AdaptiveComponentInstanceUtils.SetInstanceFlipped (temp_instance, True)
        rotation = DB.Transform.CreateRotationAtPoint (axis, math.pi, pt) * rotation


    axis = rotation.BasisY
    angle = rotate_angle_y
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation
    if reflection and use_UV_projection:
        DB.AdaptiveComponentInstanceUtils.SetInstanceFlipped (temp_instance, True)
        rotation = DB.Transform.CreateRotationAtPoint (axis, math.pi, pt) * rotation


    axis = rotation.BasisX
    angle = rotate_angle_x
    pt = DB.XYZ(0, 0, 0)
    rotation = DB.Transform.CreateRotationAtPoint (axis, angle, pt) * rotation
        


    translation = DB.Transform.CreateTranslation(DB.XYZ(X, Y, Z))
    total_transform = translation * rotation


    # if use non- adaptive generic model then modify this.
    insert_pt = DB.AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(temp_instance)[0]
    actual_Z = doc.GetElement(insert_pt).Position.Z
    if reflection:
        additional_translation = DB.Transform.CreateTranslation(DB.XYZ(0, 0, actual_Z))
    else:
        additional_translation = DB.Transform.CreateTranslation(DB.XYZ(0, 0, -actual_Z))
    total_transform = additional_translation * total_transform
    
    DB.AdaptiveComponentInstanceUtils.MoveAdaptiveComponentInstance (temp_instance , total_transform, True)

    return temp_instance

################## main code below #####################
if __name__ == "__main__":
    block2family()







