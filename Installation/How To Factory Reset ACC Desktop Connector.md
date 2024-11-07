# Factory Reset Instructions for ACC Desktop Connector

⚠️ **WARNING**: This process will delete all local changes that have not been uploaded to the server. Make sure to save out any important work in a local location before proceeding. Later you can move them back to ACC desktop connector to retry upload.

## Steps to Reset

1. **Shutdown ACC Desktop Connector**
   - Close the application completely

2. **Clean Up User Folders** 
   Delete the following folders:
   - Main DC folder: `C:\Users\[UserName]\DC`
   - Local data: `C:\Users\[UserName]\AppData\Local\Autodesk\Desktop Connector\Data`
   - Session data: `C:\Users\[UserName]\AppData\Local\Autodesk\DesktopConnector.Applicat_Url_[LongRandomString]`

3. **Run Cleanup Utility**
   - Execute `ShellCleanup.exe` located at:
   - `C:\Program Files\Autodesk\Desktop Connector\ShellCleanup.exe`
   - This will remove the Autodesk Blue Icon from File Explorer

4. **Restart Application**
   - Launch ACC Desktop Connector again
