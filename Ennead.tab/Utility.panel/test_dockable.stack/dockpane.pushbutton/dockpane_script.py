__context__ = "zero-doc"


import os.path as op

from pyrevit import HOST_APP, framework
from pyrevit import DB
from pyrevit import forms

from pyrevit.framework import wpf, ObservableCollection
import EnneadTab

def docopened_eventhandler(sender, args):
    print (args.Document)
    forms.alert("Doc Opened" + args.Document)

HOST_APP.app.DocumentOpened += \
    framework.EventHandler[DB.Events.DocumentOpenedEventArgs](
        docopened_eventhandler
        )


class DockableExample(forms.WPFPanel):
    panel_title = "pyRevit Dockable Panel Title"
    panel_id = "3410e336-f81c-4927-87da-4e0d30d4d64a"
    panel_source = op.join(op.dirname(__file__), "DockableSheets2.xaml")

    def __init__(self):
      wpf.LoadComponent(self, self.panel_source)
      self.thread_id = framework.get_current_thread_id()
      self.title.Text = "Sheets in Model"

    def button_refresh(self, sender, args):
      self.update_list()

    def update_list(self):
      try:
        sheets = DB.FilteredElementCollector(HOST_APP.doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        sheets = [s.Title for s in sheets if not s.IsPlaceholder]
        sheets.sort()
        template_list = [forms.TemplateListItem(s) for s in sheets]
        #self.list_lb.ItemsSource = ObservableCollection[forms.TemplateListItem](template_list)
      except Exception as e:
        print (e.message)


@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
  forms.register_dockable_panel(DockableExample)
  
if __name__ == '__main__':
  main()
