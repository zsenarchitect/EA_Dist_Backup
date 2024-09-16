# How to Install EnneadTab

## 1. Setup Basic
### 1.0 Remove Existing Ecosys Folder
If you have "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem", delete ecosystem folder just to get a clean reinstall.

> [!IMPORTANT]
> If you are using One-Drive, please note that you usually have __two__ Documents folders at your computer, see samples below. For all future reference, we will be talking about the non-One-Drive folder.
> - C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem :thumbsup:
> - C:\Users\\[USER_NAME]\OneDrive - Ennead Architects\Documents\EnneadTab Ecosystem :thumbsdown:


<br>
<br>


### 1.1 Download Installer
Download "EnneadTab_OS_Installer.exe" from link below. Save anywhere.

- https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_core.png)


> [!NOTE]
> Some computer's firewall(such as windows smart defender) might mark this exe as potential virus, but it is really NOT virus, I promise! Just continue download and save that exe file. If for whatever reason your firewall still reject the download, use below L drive location as a backup.
> - "L:\4b_Applied Computing\EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe"

<br>
<br>

### 1.2 Install Ecosystem Folder
Run the installer you just downloaded. It might takes a few seconds (or minutes, depending on your internet speed) to unpack the contents. 
![os install in progress](/Apps/lib/EnneadTab/images/Instruction_getting_OS.png)

Watch the progress, when it says finished it will close itself, and it is ready to move on installing Rhino and Revit Version. Follow __step 2.1 or 3.1__ below.


<br>
<br>

## 2. EnneadTab-For-Revit


### 2.1. EnneadTab-For-Revit 2.0
0. EnneadTab-For-Revit run over pyRevit framework. Make sure you have pyrevit installed. Revit is not open.
You can get pyrevit from here and pick the first one under "Download" section. There is no admin restriction to install: https://github.com/pyrevitlabs/pyRevit/releases

1. No need to uninstall old version of EnneadTab-For-Revit, it will be handled automatically.

2. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"

3. Make sure no Revit is running during the installation.
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

> [!NOTE]
> Attention, __Rhino 8__ users!
> <br>
> Due to the significant .Net framework changes from Rhino 7 to 8, you will need to configure your Rhino 8 to be backward compatable before installing EnneadTab-for-Rhino. Please do the following: <br>
> 1. Start __ONE__ Rhino for Windows<br>
> 2. Type the command __SetDotNetRuntime__<br>
> 3. Select the __Runtime__ option<br>
> 4. Set the __NETFramework__ option<br>
> 5. Close Rhino<br>




### 3.1 EnnneaTab-For-Rhino 2.0
0. Troughly uninstall __any__ previous EnneadTab-For-Rhino version by following __step 3.2__, ignore if you have no previous version.
1. Navigate to 
    - "C:\Users\\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation"
2. Have only ONE Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window(If you cannot see it, you system might not display file extension such as .rui)
3. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
4. Restart Rhino.


> [!IMPORTANT]
> Rhino only remember the setting of most recent closed Rhino. Using only one rhino help to make installation stick.

> [!TIP]
> After restart, every button should work just fine, But if you see error message such as "Cannot find EnneadTab" or "No module named Ennead.xxx", hit __GetLatest__ from dropdown menu usually fix it.


### 3.2 Unistall Ennead-For-Rhino
With __only one Rhino__ is open, remove any old EnneadTab Rhino by using command "_Toolbar", then close any toolbar that mentions "EnneadTab". Most cases there should be only one mentioning, but certain OG users might see two. Close them all. No need to save any toolbar. __RESTART RHINO__ so any trace of it is completely removed from session. Now you have completely removed EnneadTab-Rhino.

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_remove_old_rui.png)

## 4. Configure Notification Level
EnneadTab comes with many functions to help your task. It also provide many notification for long process time event, such as heavy exporting and family loading, so you are are more aware of the status of the workflow.

By default, EnneadTab set default amount of notification. But you can set it to be __no notification__ or __more notification__ by going to the __Setting__ in EnneadTab Revit. 

![screenshot of EnneadTab Revit Setting](/Apps/lib/EnneadTab/images/Instruction_setting.png)


Those setting will affect both Revit and Rhino, but since the majority notification happens from Revit side, this setting is only configerable in Revit side.


