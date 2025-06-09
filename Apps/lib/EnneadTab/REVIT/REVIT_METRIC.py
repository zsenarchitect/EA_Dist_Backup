from datetime import datetime
import DATA_FILE
import EMAIL
PREFIX = "REVIT_METRIC"

class RevitMetric:
    def __init__(self, doc):
        self.doc = doc

    def update_metric(self):
        data_file_name = "{}_{}".format(PREFIX, self.doc.Title)
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DATA_FILE.update_data(data_file_name, is_local=False) as data_file:
            if "_test" not in data_file:
                data_file["_test"] = []
            
            data_file["_test"].append(report_time)

        EMAIL.email_to_self(
            subject="REVIT_METRIC",
            body="placeholder report: {} has been generated at {}".format(self.doc.Title, report_time)
        )




