# How to Install EnneadTab


## 1. Setup Basic
If you have "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem", delete ecosystem folder just to get a clean reinstall.

Download "EnneadTab_OS_Installer.exe" from link below.

- https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe

Save anywhere and run it. It might takes a few seconds( or minutes, depending on your download speed) to unpack the contents. 

When you can see "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation" then it is ready to move on installing Rhino and Revit Version. Follow __step 2.2 or 3.2__ below.
![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_core.png)

> [!NOTE]
> Some computer's firewall might mark this exe as potential virus, but it is really NOT virus, I promise! Just continue download and save that exe file. If for whatever reason your firewall still reject the download, use below L drive location as a backup.
- "L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe"
     

Legacy version use script hosted by L drive version. Legacy version only works with other legacy version. There are no plan to further improve any legacy version.

## 2.1. EnneadTab-For-Revit(Legacy)
1. Make sure you have pyrevit installed. Revit is not open.

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Double click on 
    - "EnneadTab-For-Revit(Legacy).exe"

4. You can now open Revit.

## 2.2. EnneadTab-For-Revit 2.0
1. Make sure you have pyrevit installed. Revit is not open.
You can get pyrevit from here, there is no admin restriction: https://github.com/pyrevitlabs/pyRevit/releases

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Double click on 
    - "EnneadTab-For-Revit.exe"

4. You can now open Revit.

5. __(Optional)__ Configer your notification level at chapter 4 below.

## 2.3 Uninstall Ennead-For-Revit

1. Revit is not open.

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Double click on 
    - "EnneadTab_For_Revit_UnInstaller.exe"

4. You can now open Revit.

## 3.1 EnnneaTab-For-Rhino(Legacy)
(No plan to distribute/maintain)


## 3.2 EnnneaTab-For-Rhino 2.0
0. Troughly uninstall __any__ previous version by following __step 3.3__, ignore if you have no previous version.
1. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
2. Have only ONE Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window
3. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
4. Restart Rhino.


> [!IMPORTANT]
> Rhino only remember the setting of most recent closed Rhino. Using only one rhino help to make installation stick.

> [!TIP]
> After restart, every button should work just fine, But if you see error message such as "Cannot find EnneadTab", hit __GetLatest__ usually fix it.

## 3.3 Unistall Ennead-For-Rhino
With __only one Rhino__ is open, remove any old EnneadTab Rhino by using command "_Toolbar", then close any toolbar that mentions "EnneadTab". Most cases there should be only one mentioning, but certain OG users might see two. Close them all. No need to save any toolbar. __RESTART RHINO__ so any trace of it is completely removed from session. Now you have completely removed EnneadTab-Rhino.

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_remove_old_rui.png)

## 4. Configer Notification Level
EnneadTab comes with many functions to help your task. It also provide many notification for long process time event, such as heavy exporting and family loading, so you are are more aware of the status of the workflow.

By default, EnneadTab set default amount of notification. But you can set it to be __no notification__ or __more notification__ by going to the __Setting__ in EnneadTab Revit. 

![screenshot of EnneadTab Revit Setting](/Apps/lib/EnneadTab/images/Instruction_setting.png)


