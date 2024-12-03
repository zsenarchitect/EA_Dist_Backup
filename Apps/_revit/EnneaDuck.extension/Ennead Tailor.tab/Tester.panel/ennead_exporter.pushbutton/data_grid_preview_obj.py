from EnneadTab import NOTIFICATION


class DataGridPreviewObj(object):
    @staticmethod # making this a independent function to the class, not to instance obj
    def legalize_filename( name):
        if r"/" in name:
            pass#print "Windows file name cannot contain '/' in its name, i will replace it with '-'"
        if "*" in name:
            NOTIFICATION.messenger (main_text="* is found in <{}>. Better remove this.".format(name))
        return name.replace("/", "-")#.replace("*","")


    def __init__(self, view_or_sheet, file_id, index, extension, time_estimate, is_in_height_light_zone = False, is_sheet_group_prefix = False):

        # used to show zone in datagrid when there is more than one doc to print
        self.is_in_height_light_zone = is_in_height_light_zone


        if view_or_sheet is None:# used when initiating empty grid
            self.format_name = "XXX"
            self.time_estimate = 0
            self.extension = ".X"
            return
        self.item = view_or_sheet
        self.file_id = file_id
        self.index = index
        #self.__raw_name = "To be filled at runn time"
        self.extension = extension
        self.time_estimate = time_estimate
        self.sheet_name = DataGridPreviewObj.legalize_filename(view_or_sheet.Name)
        self.sheet_number = DataGridPreviewObj.legalize_filename(view_or_sheet.SheetNumber)



        if file_id is None:# used when not using file id prefix
            self.format_name = "{} - {}{}".format(self.sheet_number,
                                                self.sheet_name,
                                                extension)
        else:
            self.format_name = "{}_{}_{} - {}{}".format(file_id,
                                                        index,
                                                        self.sheet_number,
                                                        self.sheet_name,
                                                        extension)


        if is_sheet_group_prefix:
            # have to assume non-EA file has no such parameters
            sheet_group = self.item.LookupParameter("Sheet_$Group").AsString() if self.item.LookupParameter("Sheet_$Group") else "Sheet $Group Missing"
            sheet_series = self.item.LookupParameter("Sheet_$Series").AsString() if self.item.LookupParameter("Sheet_$Series") else "Sheet $Series Missing"

            self.format_name = "[{}]-[{}]_{} - {}{}".format(sheet_group,
                                                            sheet_series,
                                                            self.sheet_number,
                                                                self.sheet_name, 
                                                                extension)


    @property
    def raw_name(self):
        return self.format_name.replace(self.extension, "")


    @property
    def time_estimate_format(self):


        if self.time_estimate == 0:
            return "N/A"
        if int(self.time_estimate) < 60:
            return "{:.2f} s".format(self.time_estimate * 1.0)

        return "{:.2f} mins".format(self.time_estimate / 60.0)
    """
    @raw_name.setter
    def raw_name(self, val):
        self.__raw_name == self.format_name.replace(self.extension, "")

    @raw_name.deleter
    def raw_name(self, val):
        del self.__raw_name
    """

    def __str__(self):
        return "Preview_Object: {}".format(self.format_name)