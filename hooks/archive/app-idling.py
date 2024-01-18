
"""
if idling for too long it warns
"""
from pyrevit import forms, script
from pyrevit import EXEC_PARAMS
import datetime
import time
"""
' Create a text note and update it once per second while Revit is idle
Private textNote As TextNote = Nothing
Private oldDateTime As [String] = Nothing
Public Function Execute(commandData As ExternalCommandData, ByRef message As String, elements As ElementSet) As Autodesk.Revit.UI.Result Implements IExternalCommand.Execute
    Dim uiApp As New UIApplication(commandData.Application.Application)
    Dim doc As Document = commandData.Application.ActiveUIDocument.Document
    Using t As New Transaction(doc, "Text Note Creation")
        t.Start()
        oldDateTime = DateTime.Now.ToString()
        Dim defaultTextTypeId As ElementId = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
        textNote = textNote.Create(doc, doc.ActiveView.Id, XYZ.Zero, oldDateTime, defaultTextTypeId)
        t.Commit()
    End Using
    AddHandler uiApp.Idling, AddressOf idleUpdate
    Return Result.Succeeded
End Function
Public Sub idleUpdate(sender As Object, e As IdlingEventArgs)
    Dim uiApp As UIApplication = TryCast(sender, UIApplication)
    Dim doc As Document = uiApp.ActiveUIDocument.Document
    If oldDateTime <> DateTime.Now.ToString() Then
        Using transaction As New Transaction(doc, "Text Note Update")
            transaction.Start()
            textNote.Text = DateTime.Now.ToString()
            transaction.Commit()
        End Using
        oldDateTime = DateTime.Now.ToString()
    End If
End Sub
"""
#############  main    ###########



UIApplication = EXEC_PARAMS.event_args

#doc = UIApplication.ActiveUIDocument.Documents[0]
'''
try:
    #print UIApplication.Application
    doc = UIApplication.Application.Document
except Exception as e:
    print (e)
finally:
    print "fail"
'''
output = script.get_output()
#output.close_others()

life_span = 10
old_time = time.strftime("%S")


if int(old_time ) % life_span == 0:

    from pyrevit import revit, DB
    import math
    doc = revit.doc
    texts = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(DB.TextNote).WhereElementIsNotElementType().ToElements()
    if texts[0].Text == str(old_time):
        script.exit()
    print old_time
    print "every {} seconds".format(life_span)
    with revit.Transaction("temp"):

        for text in texts:
            text.Text = str(old_time)
            #DB.ElementTransformUtils().MoveElement(doc, line.Id, DB.XYZ(math.sin(old_time),math.cos(old_time),0))
#new_time = time.time()
#print new_time


output = script.get_output()
output.self_destruct(life_span)
#output.close_others()
