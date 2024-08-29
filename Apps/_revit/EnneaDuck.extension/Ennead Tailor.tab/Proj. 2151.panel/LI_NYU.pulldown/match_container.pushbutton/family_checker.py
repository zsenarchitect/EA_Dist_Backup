from doctest import master
from EnneadTab import NOTIFICATION
from pyrevit import script
from Autodesk.Revit import DB # pyright: ignore 
from EnneadTab.REVIT import REVIT_FAMILY

from data_holder import TableDataHolder, ListDataHolder, SentenceDataHolder

output = script.get_output()

from match_container_script import EMOJI_DICT



class FamilyProcessor:
    def __init__(self, family_category_name, container_doc, working_docs, has_compound, is_loadable):
        NOTIFICATION.messenger("Processing [{}]".format(family_category_name))
        self.family_category_name = family_category_name
        self.container_doc = container_doc
        self.working_docs = working_docs
        self.has_compound = has_compound
        self.is_loadable = is_loadable
        self.result = []

    def update_result(self, data_holder):
        if not data_holder:
            return
        self.result.append(data_holder)

    def print_result(self):
        for data_holder in self.result:
            if isinstance(data_holder, TableDataHolder):
                data_holder.print_table()
            elif isinstance(data_holder, ListDataHolder):
                data_holder.print_collection()
            elif isinstance(data_holder, SentenceDataHolder):
                data_holder.print_sentence()
            else:
                print (data_holder)
        
    def process(self):
        self.update_result(SentenceDataHolder("# Checking Family Category {}".format(self.family_category_name)))
        category = getattr(DB.BuiltInCategory, "OST_{}".format(self.family_category_name))

        self.master_types = query_family(category, self.container_doc)
        master_type_names = sorted([_type.pretty_name for _type in self.master_types])

        # this is list of list
        self.working_doc_types_collection = [query_family(category, working_doc) for working_doc in self.working_docs]
        
        total_types = []
        total_types.extend(self.master_types)
        for working_doc_types in self.working_doc_types_collection:
            total_types.extend(working_doc_types)
        total_type_names = sorted(list(set(_type.pretty_name for _type in total_types)))

        def is_in_list(_type, _list):
            return EMOJI_DICT["Exist"] if _type in _list else EMOJI_DICT["NotExist"]
        data = []
        for type_name in total_type_names:
            row_data = [type_name, is_in_list(type_name, master_type_names)]
            for working_doc_types in self.working_doc_types_collection:
                working_doc_type_name_list = [_type.pretty_name for _type in working_doc_types]
                row_data.append(is_in_list(type_name, working_doc_type_name_list))
            data.append(row_data)

        if not data:
            self.update_result(SentenceDataHolder("## There is no such category found anywhere...\n\n___\n\n"))
            
            return

        existence_table = TableDataHolder(data=data,
                                            title="{} Type Existence Compare".format(self.family_category_name.rsplit('s', 1)[0]),
                                            columns=["{} Type".format(self.family_category_name.rsplit('s', 1)[0]), "In Container File"] + ["In [{}]".format(_doc.Title) for _doc in self.working_docs])
        self.update_result(existence_table)


        if self.is_loadable:
            self.process_version_difference()
            

        # compare all type parameter of each type BASED ON CONTAINER VERSION
        # it is ok that working doc has additional info, but inwa to to make sure AUTHERISED TYPE must be same.
        map(self.process_type_para, self.master_types)
            
        # check compund of elemet as well
        if self.has_compound:
            self.process_type_compound()

        self.update_result(SentenceDataHolder("\n\n___\n\n"))
        self.update_result(SentenceDataHolder("\n\n"))


    def process_version_difference(self):
        data = []
        bad_conditions = []
        master_family_names_checked = []
        for master_type in self.master_types:
            # some type such as FilledRegionType are part of detailcomponent category but are still considered systwm family
            if not hasattr(master_type.element, "Family"):
                continue

            # some system family such as system curtain panel cannot be edited dirrectly
            if not master_type.element.Family.IsEditable:
                continue
            family_name = master_type.family_name
            if family_name in master_family_names_checked:
                continue
            master_family_names_checked.append(family_name)
            row_data = [family_name, "---"]

            # i suspect if not activated this type cannot be loadded coorectly, even for dry load
            if not master_type.element.IsActive:
                t = DB.Transaction(master_type.element.Document, "Activate Type")
                t.Start()
                master_type.element.Activate()
                t.Commit()
                
            family_doc = master_type.element.Document.EditFamily(master_type.element.Family)
            for i, working_doc in enumerate(self.working_docs):
                is_different = REVIT_FAMILY.is_family_version_different(family_doc, working_doc)
                if is_different is None:
                    row_data.append(EMOJI_DICT["NotExist"])
                elif is_different:
                    bad_conditions.append("At <**{}**>, master version is NOT same as in <**{}**>".format(family_name, working_doc.Title))
                    row_data.append(EMOJI_DICT["NoSame"]) 
                else:
                    row_data.append(EMOJI_DICT["Same"]) 

            data.append(row_data)

            # decide to close all family at end so to not trigger doc-close hook and generate new output.
            # family_doc.Close(False)


        print_detail = len(bad_conditions)
        if print_detail:
            table = TableDataHolder(data=data,
                                    title="Version Comparision",
                                    columns=["TypeName", "Container File"] + ["[{}]".format(_doc.Title) for _doc in self.working_docs]
                                    )
            self.update_result(table)


            bad_list = ListDataHolder(data=bad_conditions)
            self.update_result(bad_list)


            gap_line = SentenceDataHolder(data="\n___\n")
            self.update_result(gap_line)




    def process_type_para(self, master_type):
        data = []
        bad_conditions = []
        for master_para in sorted(master_type.paras, key = lambda x:x.Definition.Name):
            row_data = [master_para.Definition.Name, master_para.AsValueString ()]
            
            # only add to table if there are something different, therefore worth recording, assuming everyting is fine at start and not going to record anything
            should_record_row = False 
            
            for i, working_doc_types in enumerate(self.working_doc_types_collection):
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
                                                                                                                                            self.working_docs[i].Title,
                                                                                                                                            working_doc_type_para_value))

                
                row_data.append(working_doc_type_para_value)
                
            if should_record_row:
                data.append(row_data)

        print_detail = len(bad_conditions)
        if print_detail:
            table = TableDataHolder(
                data=data,
                title="Type Detail of <**{}**>".format(master_type.pretty_name),
                columns=["Parameters", "Container File"] + ["[{}]".format(_doc.Title) for _doc in self.working_docs]
                )

            self.update_result(table)

            bad_list = ListDataHolder(data=bad_conditions)
            self.update_result(bad_list)


            gap_line = SentenceDataHolder(data="\n___\n")
            self.update_result(gap_line)

           
 

    def process_type_compound(self):
        data = []
        bad_conditions = []
        for master_type in self.master_types:
            master_compound = master_type.element.GetCompoundStructure()
            if master_compound:
                row_data = [master_type.pretty_name, "-"]
            else:
                row_data = [master_type.pretty_name,"NoCompound"]
            for i, working_doc_types in enumerate(self.working_doc_types_collection):
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
                                                                                                                                                                                                self.working_docs[i].Title))
                    row_data.append(EMOJI_DICT["NoSame"]) 
                else:
                    row_data.append(EMOJI_DICT["Same"]) 

            data.append(row_data)

        print_detail = len(bad_conditions)
        if print_detail:
            table = TableDataHolder(
                data=data,
                title="Compound Comparision",
                columns=["TypeName", "Container File"] + ["[{}]".format(_doc.Title) for _doc in self.working_docs]
            )
            self.update_result(table)

            bad_list = ListDataHolder(data=bad_conditions)
            self.update_result(bad_list)


            gap_line = SentenceDataHolder(data="\n___\n")
            self.update_result(gap_line)


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




def query_family(ost, doc):
    if "textnote" in str(ost).lower():
        NOTIFICATION.duck_pop("Querying TextNoteType")
        types = DB.FilteredElementCollector(doc).OfClass(DB.TextNoteType).WhereElementIsElementType().ToElements()
    if "dimension" in str(ost).lower():
        types = DB.FilteredElementCollector(doc).OfClass(DB.DimensionType).WhereElementIsElementType().ToElements()
    else:
        types = DB.FilteredElementCollector(doc).OfCategory(ost).WhereElementIsElementType().ToElements()
    return sorted([REVIT_FAMILY.RevitType(x) for x in types], key = lambda x: x.pretty_name)


