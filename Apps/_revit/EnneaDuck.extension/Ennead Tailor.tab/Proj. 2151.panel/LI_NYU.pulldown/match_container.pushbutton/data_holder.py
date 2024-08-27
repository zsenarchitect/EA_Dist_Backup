from pyrevit import script

class DataType:
    Table = "table"
    List = "list"
    Sentence = 'sentence'


class DataHolder(object):
    def __init__(self, data_type, data):
        self.data_type = data_type
        self.data = data


class SentenceDataHolder(DataHolder):
    def __init__(self, data):
        data_type = DataType.Sentence
        super(SentenceDataHolder, self).__init__(data_type, data)
        self.data = data

    def print_sentence(self):
        output = script.get_output()
        output.print_md(self.data)


class TableDataHolder(DataHolder):
    def __init__(self, data, title, columns):
        data_type = DataType.Table
        super(TableDataHolder, self).__init__(data_type, data)
        self.title = title
        self.columns = columns

    def print_table(self):
        output = script.get_output()
        output.print_table(table_data=self.data,
                            title=self.title,
                            columns=self.columns)


class ListDataHolder(DataHolder):
    def __init__(self, data):
        data_type = DataType.List
        super(ListDataHolder, self).__init__(data_type, data)
        self.collection = data

    def print_collection(self):
        output = script.get_output()
        for i, item in enumerate(self.collection):
            output.print_md("{} - {}".format(i+1, item))
