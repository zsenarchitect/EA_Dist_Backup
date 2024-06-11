#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now use the UI version in the same panel."
__title__ = "Merge\nFamily(Legacy)"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

class Solution:
    def merge_family(self):

        self.family_category_id = None
        # pick family types that is bad
        bad_types = self.get_family_types("you don't want to see anymore. BAAAAAAAAAAAAAAAAAAD",
                                            "Bad Types",
                                            True,
                                            is_picking_bad_type = True)
        if not bad_types:
            return


        #  pick target family
        target_type = self.get_family_types("you want to use as target.  GOOOD",
                                        "Good Type",
                                        False,
                                        is_picking_bad_type = False)
        if not target_type:
            return




        self.data = dict()
        t = DB.Transaction(doc, __title__)
        t.Start()
        for bad_type in bad_types:
            if isinstance(target_type, DB.Family):
                target_type = self.create_new_type(bad_type, target_type)



            elif not self.is_type_safe_to_merge(bad_type, target_type):
                note = "Type A = <{}>: {}\nType B = <{}>: {}\n{}".format(bad_type.Family.Name,
                                                bad_type.LookupParameter("Type Name").AsString(),
                                                target_type.Family.Name,
                                                target_type.LookupParameter("Type Name").AsString(),
                                                self.mismatch_detail)
                opts = [["Stop Merging for those two types.","Let me look at the detailed comparison."], ["Keep Merging.", "Ignore local difference, just use the tartget type data."]]
                res = EnneadTab.REVIT.REVIT_FORMS.dialogue(main_text = "There are type parameter data not matching between the two types you picked.",
                                                            sub_text = note,
                                                            options = opts)
                if not res:
                    print(1234566)
                    continue

                if res == opts[1][0]:
                    pass
                else:
                    continue

                print("######################")


            # get all instacen of bad family, first check can we get a matching type name, record all instacne data
            bad_instances = self.get_all_instance_of_type(bad_type)



            if len(bad_instances) == 0:
                print("cannot get anything from {}".format(bad_type.LookupParameter("Type Name").AsString()))
                continue

            output.print_md( "--Merging **[{}]:{}** ---> **[{}]:{}** ----Found {} Items".format(bad_type.Family.Name,
                                                    bad_type.LookupParameter("Type Name").AsString(),
                                                    target_type.Family.Name,
                                                    target_type.LookupParameter("Type Name").AsString(),
                                                    len(bad_instances)))
            #print all_instances
            map(self.process_instance_recording, bad_instances)
            #envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")
            #envvars.set_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER", DATA)

            # change them to good family by matching type name
            for bad_instance in bad_instances:
                if hasattr(bad_instance, "RoomTagType"):
                    #print "room tag"
                    bad_instance.RoomTagType = target_type
                    continue

                if hasattr(bad_instance, "AreaTagType"):
                    #print "area tag"
                    bad_instance.AreaTagType = target_type
                    continue


                if hasattr(bad_instance, "Symbol"):
                    #print "generic"
                    #print bad_instance.Category.Name
                    #print bad_instance
                    bad_instance.Symbol = target_type
                    continue

                try:
                    bad_instance.LookupParameter("Type").Set(target_type.Id)
                except Exception as e:

                    print("###Cannot change {} becasue {}".format(output.linkify(bad_instance.Id, title = bad_instance.Category.Name), e))


            # apply the data from record
            map(self.process_instance_applying, bad_instances)

            bad_family = bad_type.Family
            if len(self.get_all_instance_of_type(bad_type)) == 0:
                doc.Delete(bad_type.Id)

            #DO NOT DO this, this will purge everything
            if len( bad_family.GetFamilySymbolIds ()) == 0:
                doc.Delete(bad_family.Id)

            EnneadTab.NOTIFICATION.toast(sub_text = "",
                                        main_text = "Family Merge Finished!")


        t.Commit()

    def create_new_type(self,bad_type, target_type_family):
        sample_type = doc.GetElement(list(target_type_family.GetFamilySymbolIds ())[0])
        new_good_type = sample_type.Duplicate(bad_type.LookupParameter("Type Name").AsString())


        bad_type_paras = bad_type.Parameters
        target_type_paras = new_good_type.Parameters

        def get_para_by_name(type, name):
            for para in type.Parameters:
                if para.Definition.Name == name:
                    return para
            return None


        for bad_para in bad_type_paras:
            para_name = bad_para.Definition.Name

            if para_name in ["Family Name", "Edited by", "Workset"]:
                continue
            good_para = get_para_by_name(new_good_type, para_name)
            if not good_para:
                continue

            if good_para.IsReadOnly :
                continue

            if bad_para.StorageType == DB.StorageType.Integer:
                bad_value = bad_para.AsInteger()
                good_value = good_para.Set(bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.Double:
                bad_value = bad_para.AsDouble()
                good_value = good_para.Set(bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.String:
                bad_value = bad_para.AsString()
                # print para_name
                # print bad_value
                try:
                    id = DB.ElementId(int(bad_value))
                    good_value = good_para.Set(id)
                except:
                    good_value = good_para.SetValueString (bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.ElementId:
                bad_value = bad_para.AsElementId()
                good_value = good_para.Set(bad_value)
                continue

        return new_good_type


    def process_instance_recording(self, instance):
        # print "###############"
        # print instance
        # print instance.UniqueId
        data_entry_pack = []
        for para in instance.Parameters:
            definition = para.Definition
            # print definition.Name
            #print para.StorageType
            if para.StorageType == DB.StorageType.Integer:
                #print para.AsInteger()
                data_entry = (definition.Name, "int", para.AsInteger())
            if para.StorageType == DB.StorageType.Double:
                #print para.AsDouble()
                data_entry = (definition.Name, "dbl", para.AsDouble())
            if para.StorageType == DB.StorageType.String:
                #print para.AsString()
                data_entry = (definition.Name, "str", para.AsString())
            if para.StorageType == DB.StorageType.ElementId:
                #print para.AsElementId()
                data_entry = (definition.Name, "id", para.AsElementId())

            data_entry_pack.append(data_entry)


        #DATA[instance.Id.IntegerValue] = para
        self.data[instance.UniqueId] = data_entry_pack
        # print data_entry_pack



    def process_instance_applying(self, instance):
        # print "###############"
        #print instance
        #print instance.UniqueId
        """
        if instance.UniqueId not in self.data:
            type_name = instance.Symbol.LookupParameter("Type Name").AsString()
            family_name = instance.Symbol.FamilyName
            format_name = "{{{}}}:{}--->Cannot find matching ElementId---->{}".format(family_name, type_name, output.linkify(instance.Id, title = "Go to element"))
            print(format_name)
            return
        """
        #para = DATA[instance.Id.IntegerValue]

        # print DATA[instance.UniqueId]
        data_entry_pack = self.data[instance.UniqueId]
        for data_entry in data_entry_pack:
            #print data_entry
            para_name, para_type, value = data_entry

            #definition = para.Definition
            #print definition.Name
            #print para.StorageType
            """
            if para.StorageType == DB.StorageType.Integer:
                #print para.AsInteger()
                value = para.AsInteger()
            if para.StorageType == DB.StorageType.Double:
                #print para.AsDouble()
                value = para.AsDouble()
            if para.StorageType == DB.StorageType.String:
                #print para.AsString()
                value = para.AsString()
            if para.StorageType == DB.StorageType.ElementId:
                #print para.AsElementId()
                value = para.AsElementId()
            """
            if para_name in ["Type Id", "Type", 'Family and Type', "Family"]:
                #print "Skip assinging those parameter: {}".format(para_name)
                continue
            para = instance.LookupParameter(para_name)

            if not para:
                print("No matching instance parameter to apply: {}".format(para_name))
                continue

            if para.IsReadOnly:
                #print "<" + para_name + "> is read-only"
                continue


            if value is None:
                pass
                #print "Skip assinging those parameter if has no value in record: {}".format(para_name)
            try:
                para.Set(value)
            except Exception as e:
                pass
                #print "Cannot assign {} becasue: {}".format(para_name, e)

    def get_all_instance_of_type(self, type):

        type_filter = DB.FamilyInstanceFilter (doc, type.Id)
        instances = list(DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())

        """
        area_tag_type_filter = DB.AreaTagFilter  ()
        area_tag_type_filter.PassesFilter()
        area_tags = list(DB.FilteredElementCollector(doc).OfClass(DB.SpatialElementTag ).WherePasses (area_tag_type_filter).ToElements())

        room_tag_type_filter = DB.AreaTagFilter  ()
        room_tags = list(DB.FilteredElementCollector(doc).OfClass(DB.SpatialElementTag ).WherePasses (room_tag_type_filter).ToElements())

        instances.extend(area_tags)
        instances.extend(room_tags)
        """
        independent_tags = list(DB.FilteredElementCollector(doc).OfClass(DB.IndependentTag  ).WhereElementIsNotElementType().ToElements())
        independent_tags = filter(lambda x: x.GetTypeId() == type.Id, independent_tags)


        spatial_tags = list(DB.FilteredElementCollector(doc).OfClass(DB.SpatialElementTag ).WhereElementIsNotElementType().ToElements())


        def is_match_type(x):
            if hasattr(x, "RoomTagType"):
                return x.RoomTagType.Id == type.Id

            if hasattr(x, "AreaTagType"):
                return x.AreaTagType.Id == type.Id

            return False

        spatial_tags = filter(is_match_type, spatial_tags)

        instances.extend(spatial_tags)
        instances.extend(independent_tags)
        return instances

    def get_family_types(self, title, bt_name, is_multiple, is_picking_bad_type):


        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).WhereElementIsNotElementType().ToElements()
        families = sorted(families, key = lambda x: x.Name.lower())
        if self.family_category_id is not None:
            families = filter(lambda x: x.FamilyCategoryId == self.family_category_id, families)

        family = forms.SelectFromList.show(families,
                                            multiselect = False,
                                            name_attr = 'Name',
                                            width = 1000,
                                            title = "Pick family {}".format(title),
                                            button_name = 'Select Family {}'.format(bt_name))
        if not family:
            return

        self.family_category_id = family.FamilyCategoryId



        types = [doc.GetElement(x) for x in family.GetFamilySymbolIds ()]
        types = sorted(types, key = lambda x: x.LookupParameter("Type Name").AsString())
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}]: {}".format(self.FamilyName, self.LookupParameter("Type Name").AsString())
        types = [MyOption(x) for x in types]
        if not is_picking_bad_type:
            types.append("<Create type based on the bad type>")
        family_type = forms.SelectFromList.show(types,
                                                multiselect = is_multiple,
                                                width = 1000,
                                                title = "Pick type {} from family {}".format(title, family.Name),
                                                button_name = 'Select {}'.format(bt_name))


        if isinstance(family_type, str):
            return family
        return family_type


    def is_type_safe_to_merge(self, bad_type, target_type):
        self.mismatch_detail = ""

        bad_type_paras = bad_type.Parameters
        target_type_paras = target_type.Parameters

        def get_para_by_name(type, name):
            for para in type.Parameters:
                if para.Definition.Name == name:
                    return para
            return None

        def is_detail_checked(para_name, bad_value, good_value):
            if bad_value == good_value:
                return True
            #print "Type Value Difference between bad type and target type: <{}>: {} VS {}".format(para_name, bad_value, good_value)
            note = "\n\nType A: Type Value <{}> = {}".format(para_name, bad_value)
            note += "\nType B: Type Value <{}> = {}".format(para_name,  good_value)
            print(note)
            self.mismatch_detail += note
            return False


        found_mismatch = False
        for bad_para in bad_type_paras:
            para_name = bad_para.Definition.Name
            if para_name in ["Family Name", "Edited by", "Workset"]:
                continue
            good_para = get_para_by_name(target_type, para_name)
            if not good_para:
                continue

            if bad_para.StorageType == DB.StorageType.Integer:
                bad_value = bad_para.AsInteger()
                good_value = good_para.AsInteger()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.Double:
                bad_value = bad_para.AsDouble()
                good_value = good_para.AsDouble()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.String:
                bad_value = bad_para.AsString()
                good_value = good_para.AsString()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.ElementId:
                bad_value = bad_para.AsElementId()
                good_value = good_para.AsElementId()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue


        if found_mismatch:
            print("Please beaware there are mismatch of type parameter between <{}>:{} and <{}>:{}".format(bad_type.Family.Name,
                                                                                                        bad_type.LookupParameter("Type Name").AsString(),
                                                                                                        target_type.Family.Name,
                                                                                                        target_type.LookupParameter("Type Name").AsString()))
            return False
        return True



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    Solution().merge_family()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
