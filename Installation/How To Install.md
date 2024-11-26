# How to Install EnneadTab

## 1. Setup Basic
### 1.0 Remove Existing Ecosys Folder
If you have "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem", delete ecosystem folder just to get a clean reinstall.

> [!IMPORTANT]
> If you are using One-Drive, please note that you usually have __two__ Documents folders at your computer, see samples below. For all future reference, we will be talking about the non-One-Drive folder.
> - C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem :thumbsup:
> - C:\Users\\[USER_NAME]\OneDrive - Ennead Architects\Documents\EnneadTab Ecosystem :thumbsdown: This should not exist, if so, delete it.


<br>
<br>


### 1.1 Download Installer
Sometime your drive cannot connect to L drive after computer is restarted.(The little red X symbol on your drive icon). You can reconnect it by double clicking on that drive icon.

If you can connect to L drive, go this and ignore rest of step __1.1__
> - L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe

Otherwise, see link below to download "EnneadTab_OS_Installer.exe". Save anywhere.

- https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_core.png)

> [!TIP]
> Unconfirmed.crdownload file is a partial download file. Your chrome is working hard to download, do not attempt to unzip it, run it, or drag it to Rhino. Just wait for it to be fully downloaded and become __EnneadTab_OS_Installer.exe__


> [!NOTE]
> Some computer's firewall(such as windows smart defender) might mark this exe as potential virus, but it is really NOT virus, I promise! Just continue download and save that exe file. If for whatever reason your firewall still reject the download, or your firewall refuse to run the exe, run exe from below L drive location as a backup plan.
> - "L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe"

<br>
<br>

### 1.2 Install Ecosystem Folder
Run the installer you just downloaded by double clicking the exe file. It might takes a few seconds (or minutes, depending on your internet speed) to unpack the contents. __This window will only show if there was no existing Ecosystem folder, aka a clean (re)installation. Otherwise it will be a silent installation, and you can move on to next step when you have the needed content.__
![os install in progress](/Apps/lib/EnneadTab/images/Instruction_getting_OS.png)

Watch the progress, when it says finished it will close itself, and it is ready to move on installing Rhino and Revit Version. Follow __step 2.1 or 3.1__ below.


<br>
<br>

## 2. EnneadTab-For-Revit
> [!NOTE]
> Attention, __Revit 2025__ users!
> <br>
> Due to the significant .Net framework changes from 2024 to 2025, pyRevit is not yet supported for Revit 2025. <br>
> Therefore, EnneadTab-For-Revit is not supported for Revit 2025 yet. Please check back later.


### 2.1. EnneadTab-For-Revit
0. EnneadTab-For-Revit run over pyRevit framework. Make sure you have pyrevit installed. 
You can get pyrevit from here and pick the first one under "Download" section. There is no admin restriction to install: https://github.com/pyrevitlabs/pyRevit/releases

1. No need to uninstall old version of EnneadTab-For-Revit, it will be handled automatically.

2. Make sure no Revit is running during the installation.

3. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

4. Double click on 
    - "EnneadTab-For-Revit.exe"(If you cannot see it, you system might not display file extension such as .exe)

5. You can now open Revit.

6. __(Optional)__ Configure your Revit's notification level at chapter 4 below.



### 2.2 Uninstall Ennead-For-Revit

1. Revit is not open.

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Double click on 
    - "EnneadTab_For_Revit_UnInstaller.exe"(If you cannot see it, you system might not display file extension such as .exe)

4. You can now open Revit.

<br>
<br>

## 3 EnnneaTab-For-Rhino

### 3.1 EnnneaTab-For-Rhino 7
0. Troughly uninstall __any__ previous EnneadTab-For-Rhino version by following __step 3.3__, ignore if you have no previous version.
1. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
2. Have __ONLY ONE__ Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window.
3. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
4. Restart Rhino.

### 3.2 EnnneaTab-For-Rhino 8
> [!NOTE]
> Attention, __Rhino 8__ users!
> <br>
> Due to the significant .Net framework changes from Rhino 7 to 8, you will need to configure your Rhino 8 to be backward compatable before installing EnneadTab-for-Rhino. Therefore, compared to the installation of EnneadTab-for-Rhino 7, you will need to do a few more steps.


0. Troughly uninstall __any__ previous EnneadTab-For-Rhino version by following __step 3.3__, ignore if you have no previous version.
1. If you have not done this before, start __ONLY ONE__ Rhino for Windows, type the command __SetDotNetRuntime__, select the __Runtime__ option. Set the __NETFramework__ option. Close Rhino.
2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
3. Have __ONLY ONE__ Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window.
4. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
5. You will see that the side bar is not showing up, this is becasue Rhino 8 has made some change compared to 7 that affect how toolbar is loaded. Now is to go to below setting of Rhino and click different checkboxes to make Rhino load, at the end of action just make sure to check the Group: Dynamic Rui at the end.
![screenshot of toggle r8 sidebar](/Apps/lib/EnneadTab/images/Instruction_toggle_r8_sidebar.png)
6. Restart Rhino.


> [!IMPORTANT]
> Rhino only remember the setting of most recent closed Rhino. Using only one rhino help to make installation stick.

> [!TIP]
> After restart, every button should work just fine, But if you see error message such as "Cannot find EnneadTab" or "No module named Ennead.xxx", hit __ActivateEnneadTab__ from dropdown menu usually fix it.<br>
> ![screenshot of activation](/Apps/lib/EnneadTab/images/instruction_activate_rhino.png)


### 3.3 Unistall Ennead-For-Rhino
With __only one Rhino__ is open, remove any old EnneadTab Rhino by using command "_Toolbar", then close any toolbar that mentions "EnneadTab". Most cases there should be only one mentioning, but certain OG users might see two. Close them all. No need to save any toolbar. __RESTART RHINO__ so any trace of it is completely removed from session. Now you have completely removed EnneadTab-Rhino.

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_remove_old_rui.png)

## 4. Configure Notification Level
EnneadTab comes with many functions to help your task. It also provide many notification for long process time event, such as heavy exporting and family loading, so you are are more aware of the status of the workflow.

By default, EnneadTab set default amount of notification. But you can set it to be __no notification__ or __more notification__ by going to the __Setting__ in EnneadTab Revit. 

![screenshot of EnneadTab Revit Setting](/Apps/lib/EnneadTab/images/Instruction_setting.png)


Those setting will affect both Revit and Rhino, but since the majority notification happens from Revit side, this setting is only configerable in Revit side.


