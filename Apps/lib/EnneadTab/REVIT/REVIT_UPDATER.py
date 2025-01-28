"""not to be confused with the repo updater for updating by git


https://discourse.pyrevitlabs.io/t/dynamic-model-updater-and-revit-events/1593
here is a good example of using the updater to register a customized event


thi si s to make a super Eventbased updater for revit
"""


try:
    from System import Guid # pyright: ignore
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass

# Define the EnneadTabUpdater
class EnneadTabUpdater(DB.IUpdater):
    def Execute(self, data):
        print("Updater was triggered!")
        
    def GetUpdaterId(self):
        # Return the unique identifier for this updater
        return self.updater_id

    def GetUpdaterName(self):
        return 'EnneadTabUpdaterName'

    def GetAdditionalInformation(self):
        return 'A simple updater for testing purposes'

    def GetChangePriority(self):
        """https://www.revitapidocs.com/2023/9db16841-106b-23bb-0c29-42017edcf69f.htm
        more exmaple of all enumeration"""
        return DB.ChangePriority.Annotations

    def Initialize(self):
        # This is where you can add trigger conditions for the updater
        pass

    def Uninitialize(self):
        pass


if __name__ == "__main__":
    # Get the current document and application
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
    app = __revit__.Application # pyright: ignore

    # Create an instance of the updater
    updater = EnneadTabUpdater()

    # Create a unique Guid for the updater
    guid = Guid.NewGuid()

    # Create an UpdaterId using the AddInId of the current application and the unique Guid
    updater_id = DB.UpdaterId(app.ActiveAddInId, guid)

    # Set the identifier in the updater instance
    updater.updater_id = updater_id

    # Register the updater with a trigger for wall elements
    if not DB.UpdaterRegistry.IsUpdaterRegistered(updater_id, doc):
        DB.UpdaterRegistry.RegisterUpdater(updater, doc)
        
        # Create a filter for wall elements
        wall_filter = DB.ElementCategoryFilter(DB.BuiltInCategory.OST_Walls)
        
        # Assign the trigger to the updater for element updates
        DB.UpdaterRegistry.AddTrigger(updater_id, wall_filter, DB.Element.GetChangeTypeGeometry())
        
        print('Success', 'Updater has been registered and trigger has been set!')
    else:
        print('Notice', 'Updater is already registered.')