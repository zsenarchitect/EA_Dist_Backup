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
Depending on your network access, you can use the installer from Ennead Network or download from GitHub. __You do not need to do both__.
#### 1.1.a From inside Ennead Network
Run this installer from L drive.
> - L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe

<br>
<br>

#### 1.1.b From GitHub
See link below to download "EnneadTab_OS_Installer.exe". Save anywhere. Use this method for computer without access to Ennead Network, such as your traveling laptop.

- https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_core.png)

> [!TIP]
> Unconfirmed.crdownload file is a partial download file. Your chrome is working hard to download, do not attempt to unzip it, run it, or drag it to Rhino. Just wait for it to be fully downloaded and become __EnneadTab_OS_Installer.exe__


> [!NOTE]
> Some computer's firewall(such as windows smart defender) might mark this exe as potential virus, but it is really NOT virus, I promise! Just continue download and save that exe file. 

<br>
<br>

### 1.2 Install Ecosystem Folder
Run the installer by double clicking the exe file. It might takes a few seconds (or minutes(depending on your internet speed) to unpack the contents. __This window will only show if there was no existing Ecosystem folder, aka a clean (re)installation. Otherwise it will be a silent installation, and you can move on to next step when you have the needed content.__
![os install in progress](/Apps/lib/EnneadTab/images/Instruction_getting_OS.png)

Watch the progress, when it says finished it will close itself, and it is ready to move on installing Rhino and Revit Version. Follow __step 2.1 or 3.1__ below.


<br>
<br>

## 2. EnneadTab-For-Revit

### 2.0 Prerequisite
EnneadTab-For-Revit run over __pyRevit__ framework. Make sure you have pyrevit installed before everything else.
You can get pyrevit from here and pick the first one under "Download" section. There is no admin restriction to install: https://github.com/pyrevitlabs/pyRevit/releases
> [!NOTE]
> Attention, __Revit 2025__ users!
> <br>
> Due to the significant .Net framework changes from 2024 to 2025, pyRevit stable version is not supported for Revit 2025. <br>
> Therefore, EnneadTab-For-Revit is suggested to run with 2024 and before. However if you need to work wth 2025, EnneadTab for Revit can run as long as you uninstall pyrevit 4.8 and install pyrevit 5 WIP, __it is adviced to not have both version in the same machine__. See link below for getting pyrevit 5.
> - If you have Ennead Network access: L:\4b_Applied Computing\EnneadTab-DB\pyrevit-installers\pyRevit_5.0.0.24325_signed.exe
> - Otherwise, download pyrevit 5 from here: https://www.pyrevitlabs.io/


### 2.1. EnneadTab-For-Revit

1. No need to uninstall old version of EnneadTab-For-Revit, it will be handled automatically.

2. Make sure no Revit is running during the installation.

3. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

4. Double click on 
    - "EnneadTab-For-Revit.exe"

5. You can now open Revit.

6. __(Optional)__ Configure your Revit's notification level at chapter 4 below.



### 2.2 Uninstall Ennead-For-Revit

1. Revit is not open.

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Double click on 
    - "EnneadTab_For_Revit_UnInstaller.exe"

4. You can now open Revit.

<br>
<br>

## 3 EnneadTab-For-Rhino

### 3.1 EnneadTab-For-Rhino
0. Thoroughly uninstall EnneadTab-For-Rhino 1.0 version by following __step 3.3__, ignore this step if you have no previous version. How do you know if you have previous version? If your Rhino toolbar is not saying "Ennead+" but instead saying "Ennead", you have previous version and should uninstall it first.
1. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
2. Have __ONLY ONE__ Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window.
3. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
4. (Rhino 8 only)You might see that the side bar is not showing up, this is becasue Rhino 8 has made some change compared to 7 that affect how toolbar is loaded. Now please go to below setting of Rhino and click different checkboxes randomly, such as click and unclick 'Block' collection to trigger activation and make Rhino load, but finish it in a stage like below screenshot: just make sure to check the Group: Dynamic Rui at the end.
![screenshot of toggle r8 sidebar](/Apps/lib/EnneadTab/images/Instruction_toggle_r8_sidebar.png)
5. Restart Rhino.



> [!IMPORTANT]
> Rhino only remember the setting of most recent closed Rhino. Using only one rhino help to make installation stick. 

> [!TIP]
> After restart, every button should work just fine, but if you see error message such as "Cannot find EnneadTab" or "No module named Ennead.xxx", hit __ActivateEnneadTab__ from dropdown menu usually fix it.<br>
> ![screenshot of activation](/Apps/lib/EnneadTab/images/instruction_activate_rhino.png)


### 3.2 Unistall Ennead-For-Rhino
With __only one Rhino__ is open, remove any old EnneadTab Rhino by using command "_Toolbar", then close any toolbar that mentions "EnneadTab". Most cases there should be only one mentioning, but certain OG users might see two. Close them all. No need to save any toolbar. __RESTART RHINO__ so any trace of it is completely removed from session. Now you have completely removed EnneadTab-Rhino.

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_remove_old_rui.png)

## 4. Configure Notification Level
EnneadTab comes with many functions to help with your tasks. It also provides many notifications for long process time events, such as heavy exporting and family loading, so you are more aware of the status of the workflow.

By default, EnneadTab sets a default amount of notifications. But you can set it to __no notifications__ or __more notifications__ by going to __Settings__ in EnneadTab Revit. 

![screenshot of EnneadTab Revit Setting](/Apps/lib/EnneadTab/images/Instruction_setting.png)


Those setting will affect both Revit and Rhino, but since the majority notification happens from Revit side, this setting is only configerable in Revit side.

## 5. EnneadTab-for-CAD

It is not recommended in this office to use CAD as production tool, but some time we have to work with CAD files sent from consaltants. EnneadTab-for-CAD is a tool to help you work with those CAD files. All Command begin with "EA_" prefix.

> [!NOTE]
> __EA_EXPLODE_ALL_BLOCKS__
> <br>
> Explode all blocks including nesting blocks.<br>
> If you want to import to Rhino you may consider flatterning the CAD dynamic block by this command. Otherwise you will see all version of block overlaping in Rhino.<br>
> If you are planning to import to Revit, this step is not needed.


> [!NOTE]
> __EA_DELETE_ALL_SOLID_HATCH__
> <br>
> Remove all solid hatch, inlcuding inside the blocks

> [!NOTE]
> __EA_ALL_COLOR_BY_LAYER__
> <br>
> Set all objects display color by layer

> [!NOTE]
> __EA_REMOVE_ALL_DIM__
> <br>
> Remove all dim objs

> [!NOTE]
> __EA_EXPLODE_NON_SOLID_HATCH__
> <br>
> Freeze the apperance of CAD hatch before going to Revit. <br>
> CAD hatch on small scale will become black solid in revit. There is not way around since 1985. So here this command explode the hatch into elements so its appearance is preserved regardless of the scale.

> [!NOTE]
> __EA_PREP_CAD_FOR_REVIT__
> <br>
> Quick alias for: DELETE_ALL_SOLID_HATCH + ALL_COLOR_BY_LAYER + EA_REMOVE_ALL_DIM + EA_EXPLODE_NON_SOLID_HATCH

> [!NOTE]
> __EA_PREP_CAD_FOR_RHINO__
> <br>
> Quick alias for: DELETE_ALL_SOLID_HATCH + ALL_COLOR_BY_LAYER + EA_REMOVE_ALL_DIM + EA_EXPLODE_ALL_BLOCKS + EA_EXPLODE_NON_SOLID_HATCH


### 5.1 EnneadTab-for-CAD

1. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
2. Find the file 
    - "EnneadTab_For_CAD.lsp"
3. Open CAD. Type the command 
    - "CUI"(Customize User Interface)
4. Right click on "LISP Files" and Load "EnneadTab_For_CAD.lsp"
![CAD CUI](/Apps/lib/EnneadTab/images/Instruction_cad_cui.png)
5. Restart CAD.
