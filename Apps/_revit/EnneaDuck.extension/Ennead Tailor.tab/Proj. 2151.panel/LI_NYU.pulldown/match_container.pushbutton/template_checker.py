import time
from pyrevit import script
from Autodesk.Revit import DB  # pyright: ignore
from EnneadTab.REVIT import REVIT_CATEGORY
from EnneadTab import TIME, USER
from match_container_script import EMOJI_DICT, IS_TESING_NEW_FUNC

output = script.get_output()

class TemplateProcessor:
    def __init__(self, master_template, working_doc_templates_dict, working_docs, cate_dict):
        self.master_template = master_template
        self.working_doc_templates_dict = working_doc_templates_dict
        self.working_docs = working_docs
        self.cate_dict = cate_dict
        self.is_ok = True

    def process(self):
        
        time_start = time.time()
        self.process_template_para()
        self.process_category_visibility()
        self.process_category_override()
        self.process_filter()
        self.process_workset()
        time_diff = time.time() - time_start
        output.print_md("  [**{}**] took {}.".format(self.master_template.Name, TIME.get_readable_time(time_diff)) + " Looks ok.:thumbs_up:" if self.is_ok else "")
        print ("\n\n")
        
    def process_template_para(self):
        data = []
        bad_conditions = []
        master_params = {para.Definition.Name: para.AsValueString() for para in sorted(self.master_template.Parameters, key=lambda x: x.Definition.Name)}

        for param_name, master_value in master_params.items():
            row_data = [param_name, master_value]
            should_record_row = False

            for i, doc in enumerate(self.working_docs):
                working_doc_template = self.working_doc_templates_dict[doc].get(self.master_template.Name)
                if not working_doc_template:
                    row_data.append(EMOJI_DICT["NoMatchTemplate"])
                    should_record_row = True
                    continue

                working_doc_template_para = get_matching_para(param_name, working_doc_template.Parameters)
                if not working_doc_template_para:
                    row_data.append(EMOJI_DICT["NoMatchPara"])
                    should_record_row = True
                    continue

                working_value = working_doc_template_para.AsValueString()
                if working_value != master_value and not (working_value in ["", None] and master_value in ["", None]):
                    should_record_row = True
                    bad_conditions.append(
                        "At <**{}**> 's [**{}**], master version parameter is [**{}**], and [**{}**] version is [**{}**]".format(
                            self.master_template.Name, param_name, master_value, doc.Title, working_value))

                row_data.append(working_value)

            if should_record_row:
                data.append(row_data)

        if bad_conditions:
            self.is_ok = False
            output.print_table(
                table_data=data,
                title="Template Detail of <**{}**>".format(self.master_template.Name),
                columns=["Parameters", "Container File"] + ["[{}]".format(doc.Title) for doc in self.working_docs],
            )

            for i, bad_condition in enumerate(bad_conditions):
                output.print_md("{} - {}".format(i + 1, bad_condition))

            output.print_md("\n___\n")

    def process_category_visibility(self):
        def hidden_status_to_text(is_hidden):
            return "Off" if is_hidden else "On"

        master_cate_visibilities = {
            master_cate.pretty_name: hidden_status_to_text(self.master_template.GetCategoryHidden(master_cate.category.Id))
            for master_cate in self.cate_dict[self.master_template.Document]
        }

        data, bad_conditions = [], []
        for master_cate_name, master_visibility in master_cate_visibilities.items():
            row_data = [master_cate_name, master_visibility]
            should_record_row = False

            for i, doc in enumerate(self.working_docs):
                working_doc_template = self.working_doc_templates_dict[doc].get(self.master_template.Name)
                if not working_doc_template:
                    row_data.append(EMOJI_DICT["NoMatchTemplate"])
                    should_record_row = True
                    continue

                working_doc_template_cate = get_matching_category(master_cate_name, self.cate_dict[working_doc_template.Document])
                if not working_doc_template_cate:
                    row_data.append(EMOJI_DICT["NoMatchCategory"])
                    should_record_row = True
                    continue

                working_visibility = hidden_status_to_text(working_doc_template.GetCategoryHidden(working_doc_template_cate.category.Id))
                if working_visibility != master_visibility:
                    should_record_row = True
                    bad_conditions.append(
                        "At <**{}**> 's [**{}**], master version category visibility is [**{}**], and [**{}**] version is [**{}**]".format(
                            self.master_template.Name, master_cate_name, master_visibility, doc.Title, working_visibility))

                row_data.append(working_visibility)

            if should_record_row:
                data.append(row_data)

        if bad_conditions:
            self.is_ok = False
            output.print_table(
                table_data=data,
                title="Template Category Visibility Detail of <**{}**>".format(self.master_template.Name),
                columns=["Category", "Container File"] + ["[{}]".format(doc.Title) for doc in self.working_docs],
            )

            for i, bad_condition in enumerate(bad_conditions):
                output.print_md("{} - {}".format(i + 1, bad_condition))

            output.print_md("\n___\n")

    def process_category_override(self):
        pass  # Implementation needed

    def process_filter(self):
        pass  # Implementation needed

    
    def process_workset(self):
        master_workset_visibilities = self.get_template_workset_visibilities(self.master_template)
 

        total_workset_names = []
        for x in [self.master_template.Document] + self.working_docs:
            total_workset_names.extend(TemplateProcessor.get_workset_names(x))
        total_workset_names.sort()
        
        data, bad_conditions = [], []
        for workset_name in total_workset_names:
            master_visibility = master_workset_visibilities.get(workset_name, EMOJI_DICT["NotExist"])
            row_data = [workset_name, master_visibility]
            should_record_row = False

            for i, doc in enumerate(self.working_docs):
                working_doc_template = self.working_doc_templates_dict[doc].get(self.master_template.Name)
                if not working_doc_template:
                    row_data.append(EMOJI_DICT["NoMatchWorkset"])
                    should_record_row = True
                    continue

                working_workset_visibilities = self.get_template_workset_visibilities(working_doc_template)
                working_visibility = working_workset_visibilities.get(workset_name, EMOJI_DICT["NotExist"])

                if working_visibility != master_visibility and master_visibility != EMOJI_DICT["NotExist"]: # allow master template to miss certain unused workset
                    should_record_row = True
                    bad_conditions.append(
                        "At <**{}**> 's workset [**{}**], master version visibility is [**{}**], and [**{}**] version is [**{}**]".format(
                            self.master_template.Name, workset_name, master_visibility, doc.Title, working_visibility))

                row_data.append(working_visibility)

            if should_record_row:
                data.append(row_data)

        if bad_conditions:
            self.is_ok = False
            output.print_table(
                table_data=data,
                title="Workset Visibility Detail of <**{}**>".format(self.master_template.Name),
                columns=["Workset", "Container File"] + ["[{}]".format(doc.Title) for doc in self.working_docs],
            )

            for i, bad_condition in enumerate(bad_conditions):
                output.print_md("{} - {}".format(i + 1, bad_condition))

            output.print_md("\n___\n")

    def get_template_workset_visibilities(self, template):
        workset_visibilities = {}
        doc = template.Document
        worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)

        for workset in worksets:
            visibility = template.GetWorksetVisibility(workset.Id)
            visibility_text = self.visibility_to_text(visibility)
            workset_visibilities[workset.Name] = visibility_text

        return workset_visibilities

    @staticmethod
    def get_workset_names(doc):
        worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)
        return [x.Name for x in worksets]

    def visibility_to_text(self, visibility):
        visibility_map = {
            DB.WorksetVisibility.Visible: "Visible",
            DB.WorksetVisibility.Hidden: "Hidden",
            DB.WorksetVisibility.UseGlobalSetting: "Use Global Setting"
        }
        return visibility_map.get(visibility, "Unknown")


    
def process_template(container_doc, working_docs):
    output.print_md("# Checking Template")

    master_templates = query_template(container_doc)
    if IS_TESING_NEW_FUNC:
        master_templates = master_templates[:5]
    master_template_names = {template.Name: template for template in master_templates}

    working_doc_templates_dict = {
        doc: {template.Name: template for template in query_template(doc)}
        for doc in working_docs
    }

    total_template_names = sorted(set(master_template_names.keys()).union(*[doc_templates.keys() for doc_templates in working_doc_templates_dict.values()]))

    data = [
        [template_name, EMOJI_DICT["Exist"] if template_name in master_template_names else EMOJI_DICT["NotExist"]] +
        [EMOJI_DICT["Exist"] if template_name in doc_templates else EMOJI_DICT["NotExist"] for doc_templates in working_doc_templates_dict.values()]
        for template_name in total_template_names
    ]

    output.print_table(
        table_data=data,
        title="Template Existence Compare",
        columns=["Template", "In Container File"] + ["In [{}]".format(doc.Title) for doc in working_docs],
    )

    cate_dict = {doc: get_sorted_categories(doc) for doc in [container_doc] + working_docs}
    print ("\n\n")

    for i, master_template in enumerate(master_templates):
        print ("{}/{} Checking Template [{}]...".format(i+1,len(master_templates), master_template.Name))
        processor = TemplateProcessor(master_template, working_doc_templates_dict, working_docs, cate_dict)
        processor.process()

    output.print_md("\n\n___\n\n")
    print("\n\n")


def get_sorted_categories(doc):
    categories = [
        REVIT_CATEGORY.RevitCategory(cate) for cate in doc.Settings.Categories
    ]
    categories.extend(
        REVIT_CATEGORY.RevitCategory(sub_cate) for cate in doc.Settings.Categories for sub_cate in cate.SubCategories
    )
    sorted_categories = sorted(categories, key=lambda x: x.pretty_name)
    print ("Getting {} object styles from [{}]".format(len(sorted_categories), doc.Title))
    return sorted_categories


def get_matching_category(search_name, cates):
    return next((cate for cate in cates if cate.pretty_name == search_name), None)


def get_matching_para(search_name, paras):
    return next((para for para in paras if para.Definition.Name == search_name), None)


def query_template(doc):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    all_templates = filter(lambda x: x.IsTemplate, all_views)
    return sorted(all_templates, key=lambda x: x.Name)
