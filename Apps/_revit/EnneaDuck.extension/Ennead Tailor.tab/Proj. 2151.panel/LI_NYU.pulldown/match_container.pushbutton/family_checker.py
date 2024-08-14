from pyrevit import script
from Autodesk.Revit import DB # pyright: ignore 
from EnneadTab.REVIT import REVIT_FAMILY


output = script.get_output()

from match_container_script import EMOJI_DICT

def process_family(family_category_name, container_doc, working_docs, has_compound):
    output.print_md("# Checking Family Category {}".format(family_category_name))
    category = getattr(DB.BuiltInCategory, "OST_{}".format(family_category_name))

    master_types = query_family(category, container_doc)
    master_type_names = sorted([_type.pretty_name for _type in master_types])

    # this is list of list
    working_doc_types_collection = [query_family(category, working_doc) for working_doc in working_docs]
    
    total_types = []
    total_types.extend(master_types)
    for working_doc_types in working_doc_types_collection:
        total_types.extend(working_doc_types)
    total_type_names = sorted(list(set(_type.pretty_name for _type in total_types)))

    def is_in_list(_type, _list):
        return EMOJI_DICT["Exist"] if _type in _list else EMOJI_DICT["NotExist"]
    data = []
    for type_name in total_type_names:
        row_data = [type_name, is_in_list(type_name, master_type_names)]
        for working_doc_types in working_doc_types_collection:
            working_doc_type_name_list = [_type.pretty_name for _type in working_doc_types]
            row_data.append(is_in_list(type_name, working_doc_type_name_list))
        data.append(row_data)

    if not data:
        output.print_md("## There is no such category found anywhere...\n\n___\n\n")
        return
    
    output.print_table(
        table_data=data,
        title="{} Type Existence Compare".format(family_category_name.rsplit('s', 1)[0]),
        columns=["{} Type".format(family_category_name.rsplit('s', 1)[0]), "In Container File"] + ["In [{}]".format(_doc.Title) for _doc in working_docs],
    )


    # compare all type parameter of each type BASED ON CONTAINER VERSION
    # it is ok that working doc has additional info, but inwa to to make sure AUTHERISED TYPE must be same.
    map(lambda x: process_type_para(x, working_doc_types_collection, working_docs), master_types)
        
    # check compund of elemet as well
    if has_compound:
        process_type_compound(master_types, working_doc_types_collection, working_docs)

    output.print_md ("\n\n___\n\n")
    print ("\n\n")

def process_type_para(master_type, working_doc_types_collection, working_docs):
    data = []
    bad_conditions = []
    for master_para in sorted(master_type.paras, key = lambda x:x.Definition.Name):
        row_data = [master_para.Definition.Name, master_para.AsValueString ()]
        
        # only add to table if there are something different, therefore worth recording, assuming everyting is fine at start and not going to record anything
        should_record_row = False 
        
        for i, working_doc_types in enumerate(working_doc_types_collection):
            working_doc_type = get_matching_type(master_type.pretty_name, working_doc_types)
            if not working_doc_type:
                row_data.append(EMOJI_DICT["NoMatchType"]) 
                should_record_row = True
                continue

            working_doc_type_para = get_matching_para(master_para.Definition.Name, working_doc_type.paras)
            if not working_doc_type_para:
                row_data.append(EMOJI_DICT["NoMatchPara"])
                should_record_row = True
                continue
            working_doc_type_para_value = working_doc_type_para.AsValueString ()
            if working_doc_type_para_value !=  master_para.AsValueString ():
                if working_doc_type_para_value is None and master_para.AsValueString () == "":
                    continue
                elif working_doc_type_para_value == "" and master_para.AsValueString () is None:
                    continue
                should_record_row = True
                bad_conditions.append("At <**{}**> 's [**{}**], master version parameter is [**{}**], and [**{}**] version is [**{}**]".format(master_type.pretty_name,
                                                                                                                                         master_para.Definition.Name,
                                                                                                                                         master_para.AsValueString (),
                                                                                                                                         working_docs[i].Title,
                                                                                                                                         working_doc_type_para_value))

            
            row_data.append(working_doc_type_para_value)
            
        if should_record_row:
            data.append(row_data)

    print_detail = len(bad_conditions)
    if print_detail:
        output.print_table(
            table_data=data,
            title="Type Detail of <**{}**>".format(master_type.pretty_name),
            columns=["Parameters", "Container File"] + ["[{}]".format(_doc.Title) for _doc in working_docs],
        )

        for i, bad_condition in enumerate(bad_conditions):
            output.print_md("{} - {}".format(i+1,bad_condition))

        output.print_md ("\n___\n")
 

def get_matching_para(search_name, paras):
    for para in paras:
        if para.Definition.Name == search_name:
            return para
    return None

def get_matching_type(search_name, type_list):
    for type in type_list:
        if type.pretty_name == search_name:
            return type
    return None


def process_type_compound(master_types, working_doc_types_collection, working_docs):
    data = []
    bad_conditions = []
    for master_type in master_types:
        master_compound = master_type.element.GetCompoundStructure()
        if master_compound:
            row_data = [master_type.pretty_name, "-"]
        else:
            row_data = [master_type.pretty_name,"NoCompound"]
        for i, working_doc_types in enumerate(working_doc_types_collection):
            working_doc_type = get_matching_type(master_type.pretty_name, working_doc_types)
            if not working_doc_type:
                row_data.append(EMOJI_DICT["NoMatchType"])
                continue

           
            working_doc_type_compound = working_doc_type.element.GetCompoundStructure ()
            if not working_doc_type_compound:
                row_data.append("NoCompound")
                continue
            if not master_compound.IsEqual (working_doc_type_compound ):
                bad_conditions.append("At <**{}**>, master version structure compound is NOT same as [**{}**] version. There are many thing that might be different, check carefully".format(master_type.pretty_name,
                                                                                                                                                                                            working_docs[i].Title))
                row_data.append(EMOJI_DICT["NoSame"]) 
            else:
                row_data.append(EMOJI_DICT["Same"]) 

        data.append(row_data)

    print_detail = len(bad_conditions)
    if print_detail:
        output.print_table(
            table_data=data,
            title="Compound Comparision",
            columns=["TypeName", "Container File"] + ["[{}]".format(_doc.Title) for _doc in working_docs],
        )

        for i, bad_condition in enumerate(bad_conditions):
            output.print_md("{} - {}".format(i+1,bad_condition))

        output.print_md ("\n___\n")



def query_family(ost, doc):
    if "textnote" in str(ost).lower():
        types = DB.FilteredElementCollector(doc).OfClass(DB.TextNoteType).WhereElementIsElementType().ToElements()
    if "dimension" in str(ost).lower():
        types = DB.FilteredElementCollector(doc).OfClass(DB.DimensionType).WhereElementIsElementType().ToElements()
    else:
        types = DB.FilteredElementCollector(doc).OfCategory(ost).WhereElementIsElementType().ToElements()
    return sorted([REVIT_FAMILY.RevitType(x) for x in types], key = lambda x: x.pretty_name)


