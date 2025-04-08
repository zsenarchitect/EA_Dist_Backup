from EnneadTab import USER


class DataGridDocIdMapObj(object):
    def __init__(self, doc, map_id):
        self.doc = doc
        self.doc_name = DataGridDocIdMapObj.get_central_doc_name(doc)
        self.map_id = map_id

    @staticmethod
    def get_central_doc_name(doc):
        return doc.Title.replace("_{}".format(USER.USER_NAME),  "")


if __name__ == "__main__":
    pass