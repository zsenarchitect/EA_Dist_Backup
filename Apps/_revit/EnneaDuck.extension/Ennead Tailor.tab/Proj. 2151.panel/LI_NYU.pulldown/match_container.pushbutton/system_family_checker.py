from pyrevit import script
from Autodesk.Revit import DB # pyright: ignore 
from EnneadTab.REVIT import REVIT_FAMILY

output = script.get_output()

def process_system_family(category_name, container_doc, working_docs):
    output.print_md("# Checking {}".format(category_name))
    category = getattr(DB.BuiltInCategory, "OST_{}".format(category_name))

    master_types = query_system_family(category, container_doc)
    master_type_names = sorted([_type.type_name for _type in master_types])

    # this is list of list
    working_doc_types_collection = [query_system_family(category, working_doc) for working_doc in working_docs]
    
    total_types = []
    total_types.extend(master_types)
    for working_doc_types in working_doc_types_collection:
        total_types.extend(working_doc_types)
    total_type_names = sorted(list(set(_type.type_name for _type in total_types)))

    def is_in_list(_type, _list):
        return ":OK_button:" if _type in _list else "---"
    data = []
    for type_name in total_type_names:
        row_data = [type_name, is_in_list(type_name, master_type_names)]
        for working_doc_types in working_doc_types_collection:
            working_doc_type_name_list = [_type.type_name for _type in working_doc_types]
            row_data.append(is_in_list(type_name, working_doc_type_name_list))
        data.append(row_data)
    
    output.print_table(
        table_data=data,
        title="{}Type Compare".format(category_name.rsplit('s', 1)[0]),
        columns=["{}Type".format(category_name.rsplit('s', 1)[0]), "In Container File"] + ["in [{}]".format(_doc.Title) for _doc in working_docs],
    )


    # compare all type parameter of each type BASED ON CONTAINER VERSION
    # it is ok that working doc has additional info, but inwa to to make sure AUTHERISED TYPE must be same.
    map(lambda x: process_type_para(x, working_doc_types_collection, working_docs), master_types)
        
        
    # check compund of elemet as well
    process_type_compound(master_types, working_doc_types_collection, working_docs)

    print ("\n\n\n\n")

def process_type_para(master_type, working_doc_types_collection, working_docs):
    data = []
    bad_conditions = []
    for master_para in master_type.paras:
        row_data = [master_para.Definition.Name, master_para.AsValueString ()]
        for i, working_doc_types in enumerate(working_doc_types_collection):
            working_doc_type = get_matching_type(master_type.type_name, working_doc_types)
            if not working_doc_type:
                row_data.append("NoMatchType")
                continue

            working_doc_type_para = get_matching_para(master_para.Definition.Name, working_doc_type.paras)
            if not working_doc_type_para:
                row_data.append("NoMatchPara")
                continue
            working_doc_type_para_value = working_doc_type_para.AsValueString ()
            if working_doc_type_para_value !=  master_para.AsValueString ():
                bad_conditions.append("At [**{}**] 's [**{}**], master version parameter is [**{}**], and [**{}**] version is [**{}**]".format(master_type.type_name,
                                                                                                                                         master_para.Definition.Name,
                                                                                                                                         master_para.AsValueString (),
                                                                                                                                         working_docs[i].Title,
                                                                                                                                         working_doc_type_para_value))
            row_data.append(working_doc_type_para_value)

        data.append(row_data)

    print_detail = len(bad_conditions)
    if print_detail:
        output.print_table(
            table_data=data,
            title="Type Detail of [{}]".format(master_type.type_name),
            columns=["Parameters", "Container File"] + ["[{}]".format(_doc.Title) for _doc in working_docs],
        )

    for i, bad_condition in enumerate(bad_conditions):
        output.print_md("{} - {}".format(i+1,bad_condition))

        print ("\n\n")

def get_matching_para(search_name, paras):
    for para in paras:
        if para.Definition.Name == search_name:
            return para
    return None

def get_matching_type(search_name, type_list):
    for type in type_list:
        if type.type_name == search_name:
            return type
    return None


def process_type_compound(master_types, working_doc_types_collection, working_docs):
    data = []
    bad_conditions = []
    for master_type in master_types:
        master_compound = master_type.element.GetCompoundStructure()
        if master_compound:
            row_data = [master_type.type_name, "-"]
        else:
            row_data = [master_type.type_name,"NoCompound"]
        for i, working_doc_types in enumerate(working_doc_types_collection):
            working_doc_type = get_matching_type(master_type.type_name, working_doc_types)
            if not working_doc_type:
                row_data.append("?")
                continue

           
            working_doc_type_compound = working_doc_type.element.GetCompoundStructure ()
            if not working_doc_type_compound:
                row_data.append("NoCompound")
                continue
            if not master_compound.IsEqual (working_doc_type_compound ):
                bad_conditions.append("At [**{}**], master version structure compound is NOT same as [**{}**] version. There are many thing that might be different, check carefully".format(master_type.type_name,
                                                                                                                                working_docs[i].Title))
                row_data.append("NotSame")
            else:
                row_data.append("ok")

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

        print ("\n\n")


def query_system_family(ost, doc):
    
    types = DB.FilteredElementCollector(doc).OfCategory(ost).WhereElementIsElementType().ToElements()
    return sorted([REVIT_FAMILY.RevitType(x) for x in types], key = lambda x: x.type_name)
     