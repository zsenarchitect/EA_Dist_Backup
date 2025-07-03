# How to Install EnneadTab

## Table of Contents
- [1. Overall Introduction - ABSOLUTELY Read Me First!!!!!!!!](#1-overall-introduction)
- [2. Basic Setup](#2-basic-setup)
  - [2.1 Download OS Installer](#21-download-os-installer)
  - [2.2 Install Ecosystem Folder](#22-install-ecosystem-folder)
- [3. EnneadTab for Revit](#3-enneadtab-for-revit)
  - [3.0 Prerequisite](#30-prerequisite)
  - [3.1 Install EnneadTab for Revit](#31-install-enneadtab-for-revit)
  - [3.2 Uninstall EnneadTab for Revit](#32-uninstall-enneadtab-for-revit)
- [4. EnneadTab for Rhino](#4-enneadtab-for-rhino)
  - [4.1 Install EnneadTab for Rhino](#41-install-enneadtab-for-rhino)
  - [4.2 Uninstall EnneadTab for Rhino Legacy](#42-uninstall-enneadtab-for-rhino-legacy)
- [5. Configure Notification Level](#5-configure-notification-level)
- [6. EnneadTab for CAD](#6-enneadtab-for-cad)
  - [6.1 Install EnneadTab for CAD](#61-install-enneadtab-for-cad)
- [7. Troubleshooting](#7-troubleshooting)
  - [7.1 OneDrive Synchronization Issues](#71-onedrive-synchronization-issues)
- [8. Other apps](#8-other-apps)
  - [8.1 AccFileOpenner](#81-accfileopener)
  - [8.2 DeployRevitIniFile](#82-deployrevitinifile)
  - [8.3 EnscapeAssetChanger](#83-enscapeassetchanger)
  - [8.4 LastSyncMonitor](#84-lastsyncmonitor)
  - [8.5 Pdf2indesign](#85-pdf2indesign)

## 1. Overall Introduction
Overall, you will need Ecosystem downloaded as foundation(Chapter 2). <br>
For Rhino, there is no additional requirement.<br>
For Revit, you will need pyrevit as well. (Min version 5.0.1 if planning on use for Revit 2025 and above.)

## 2. Basic Setup

> [!IMPORTANT]
> If you are using One-Drive, please note that you usually have **two** Documents folders at your computer, see samples below. For all future reference, we will be talking about the non-One-Drive folder.
> - C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem ✅
> - C:\Users\[USER_NAME]\OneDrive - Ennead Architects\Documents\EnneadTab Ecosystem ❌ 

### 2.1 Download OS Installer

Depending on your network access, you can use the installer from Ennead Network or download from GitHub. **You do not need to do both**.

#### 2.1.a From inside Ennead Network
Run this installer from L drive:
> L:\4b_Design Technology\05_EnneadTab-DB\Stand Alone Tools\EnneadTab_OS_Installer.exe

#### 2.1.b From GitHub
See link below to download "EnneadTab_OS_Installer.exe". Save anywhere. Use this method for computer without access to Ennead Network, such as your traveling laptop.

- https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_OS_Installer.exe

![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_core.png)

> [!TIP]
> Unconfirmed.crdownload file is a partial download file. Your chrome is working hard to download, do not attempt to unzip it, run it, or drag it to Rhino. Just wait for it to be fully downloaded and become **EnneadTab_OS_Installer.exe**

> [!NOTE]
> Some computer's firewall (such as windows smart defender) might mark this exe as potential virus, but it is really NOT virus, I promise! Just continue download and save that exe file.

> [!TIP]
> If your antivirus software is running high scaning those files, you can add the executable files to your antivirus whitelist using their hash values. The hash values for all executables are available in the `exe_hash.json` file located in the Installation folder. This is a more secure approach than completely disabling your antivirus.

### 2.2 Install Ecosystem Folder
Run the installer by double clicking the exe file. It might takes a few seconds (or minutes, depending on your internet speed) to unpack the contents. __This window will only show if there was no existing Ecosystem folder, aka a clean (re)installation. Otherwise it will be a silent installation, and you can move on to next step when you have the needed content.__
![os install in progress](/Apps/lib/EnneadTab/images/Instruction_getting_OS.png)



Watch the progress, when it says finished it will close itself, and it is ready to move on installing Rhino and Revit Version. Follow **step 3.1 or 4.1** below.

## 3. EnneadTab for Revit

For a complete command list of this plugin, please check [EnneadTab For Revit Handbook](https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_For_Revit_HandBook.pdf)

### 3.0 Prerequisite

EnneadTab-For-Revit run over **pyRevit** framework. Make sure you have pyrevit installed before everything else.
You can get pyrevit from here and pick the first one under "Download" section. There is no admin restriction to install: https://github.com/pyrevitlabs/pyRevit/releases

> [!NOTE]
> Attention, **Revit 2025 and above** users!  
> Due to the significant .Net framework changes from 2024 to 2025, pyRevit 4.x only support 2024 and below. pyRevit 5 will support all Revit version.  
> Make sure you have COMPLETELY removed pyrevit 4.x before adaption version **5.0.1**

### 3.1 Install EnneadTab for Revit

1. No need to uninstall old version of EnneadTab-For-Revit, it will be handled automatically.
2. Make sure no Revit is running during the installation.
3. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation`
4. Double click on `EnneadTab-For-Revit.exe`
5. You can now open Revit.
6. **(Optional)** Configure your Revit's notification level at chapter 5 below.

### 3.2 Uninstall EnneadTab for Revit

1. Revit is not open.
2. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation`
3. Double click on `EnneadTab_For_Revit_UnInstaller.exe`
4. You can now open Revit.

## 4. EnneadTab for Rhino

For a complete command list of this plugin, please check [EnneadTab For Rhino Handbook](https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/EnneadTab_For_Rhino_HandBook.pdf)

### 4.1 Install EnneadTab for Rhino

0. **(Important!)** Thoroughly uninstall EnneadTab-For-Rhino 1.0 version by following **step 4.3**, ignore this step if you have no previous version. How do you know if you have version 1.0? If your Rhino toolbar is not saying "EnneadTab" but instead saying "Ennead"/"Ennead+", you have previous version and should uninstall it first. Failed to cleanly remove old version will cause difficulty attaching new version!
1. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation`
2. Have **ONLY ONE** Rhino open, then drag "EnneadTab_For_Rhino_Installer.rui" into the Rhino window.
3. From the top of toolbar, find "Enneaaaaaaaaaaaad" menu and click on "Install".
4. **(Rhino 8 and above only)** You might see that the side bar is not showing up, this is because Rhino 8 has made some change compared to 7 that affect how toolbar is loaded. Now please go to below setting of Rhino and click different checkboxes randomly, such as click and unclick 'Block' collection to trigger activation and make Rhino load, but finish it in a stage like below screenshot: just make sure to check the Group: Dynamic Rui at the end.

![screenshot of toggle r8 sidebar](/Apps/lib/EnneadTab/images/Instruction_toggle_r8_sidebar.png)

5. Restart Rhino.

> [!IMPORTANT]
> Rhino only remember the setting of most recent closed Rhino. Using only one rhino help to make installation stick.

### 4.2 Uninstall EnneadTab for Rhino Legacy

With **only one Rhino** is open, drag in the installer.rui, use the uninstall button from the menu. Follow instruction. **RESTART RHINO** so any trace of it is completely removed from session. Now you have completely removed EnneadTab-Rhino.

## 5. Configure Notification Level

EnneadTab comes with many functions to help with your tasks. It also provides many notifications for long process time events, such as heavy exporting and family loading, so you are more aware of the status of the workflow.

By default, EnneadTab sets a default amount of notifications. But you can set it to **no notifications** or **more notifications** by going to **Settings** in EnneadTab Revit.

![screenshot of EnneadTab Revit Setting](/Apps/lib/EnneadTab/images/Instruction_setting.png)

Those setting will affect both Revit and Rhino, but since the majority notification happens from Revit side, this setting is only configurable in Revit side.

## 6. EnneadTab for CAD

It is not recommended in this office to use CAD as production tool, but some time we have to work with CAD files sent from consultants. EnneadTab-for-CAD is a tool to help you work with those CAD files. All Command begin with "EA_" prefix.

> [!TIP]
> For a video demo of what this can do.. [YouTube tutorial](https://youtu.be/KOidXxsioCg).

> [!NOTE]
> **EA_EXPLODE_ALL_BLOCKS**  
> Explode all blocks including nesting blocks.  
> If you want to import to Rhino you may consider flattening the CAD dynamic block by this command. Otherwise you will see all version of block overlapping in Rhino.  
> If you are planning to import to Revit, this step is not needed.

> [!NOTE]
> **EA_DELETE_ALL_SOLID_HATCH**  
> Remove all solid hatch, including inside the blocks

> [!NOTE]
> **EA_ALL_COLOR_BY_LAYER**  
> Set all objects display color by layer

> [!NOTE]
> **EA_REMOVE_ALL_DIM**  
> Remove all dim objs

> [!NOTE]
> **EA_EXPLODE_NON_SOLID_HATCH**  
> Freeze the appearance of CAD hatch before going to Revit.  
> CAD hatch on small scale will become black solid in revit. There is not way around since 1985. So here this command explode the hatch into elements so its appearance is preserved regardless of the scale.

> [!NOTE]
> **EA_PREP_CAD_FOR_REVIT**  
> Quick alias for: DELETE_ALL_SOLID_HATCH + ALL_COLOR_BY_LAYER + EA_REMOVE_ALL_DIM + EA_EXPLODE_NON_SOLID_HATCH

> [!NOTE]
> **EA_PREP_CAD_FOR_RHINO**  
> Quick alias for: DELETE_ALL_SOLID_HATCH + ALL_COLOR_BY_LAYER + EA_REMOVE_ALL_DIM + EA_EXPLODE_ALL_BLOCKS + EA_EXPLODE_NON_SOLID_HATCH

### 6.1 Install EnneadTab for CAD

1. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Installation`
2. Find the file `EnneadTab_For_CAD.lsp`
3. Open CAD. Type the command `CUI` (Customize User Interface)
4. Right click on "LISP Files" and Load "EnneadTab_For_CAD.lsp"

![CAD CUI](/Apps/lib/EnneadTab/images/Instruction_cad_cui.png)

5. Restart CAD.

## 7. Troubleshooting

### 7.1 OneDrive Synchronization Issues

If you find that your Documents folder Ecosystem folder is being removed periodically, this is likely due to OneDrive synchronization settings. Here's how to fix it:

1. Open OneDrive settings
2. Go to "Backup" tab
3. Click "Manage backup"
4. Uncheck the "Documents" folder from being backed up

This will prevent OneDrive from attempting to relocate your local Documents folder contents (including the Ecosystem folder) to the OneDrive Documents folder.

## 8. Other apps

### 8.1 AccFileOpenner

#### Why?
ACC Desktop Connector prioritizes the sync of Autodesk product files. For other major softwares it can sync too, **but** the connector will not sync most of the lock file. So there are risks that multiple users will override files unintentionally.

#### How to use?
![screenshot of downloading page](/Apps/lib/EnneadTab/images/Instruction_acc.png)

Keep the Openner.exe open. You can pick file/drop file to the window to make a local copy, create editing marker file on the acc folder so other users can see which file is occupied. If a second user wants to open the same file, the tool will place an edit request file to queue the editing order.

When you close file, the editing marker file is removed from acc. When a second user wants to open, their request marker file will be converted to an editing marker file.

Rhino, CAD, Indesign, Word and Excel have native lock file format that this tool can monitor. There is no action needed when exiting. Photoshop, Illustrator and PDF does not have lock file format, so you DO need to click "I am finished" to notify that you are no longer editing. The post process will handle the marker files cleanup.

The main display panel will lookup the current status of the ACC folders so you are aware where have the editing marker or request market file.

Word and Excel are preferred to edit in the cloud for its collaboration ability, but if you do need to edit it locally, the tool also allows file lock for them.

#### What file types are supported?
Files with default file lock system:
- Indesign
- Rhino
- Word
- Excel

Files without default file lock system:
- PDF
- Illustrator
- Photoshop

### 8.2 DeployRevitIniFile

This tool helps deploy Revit.ini file for all versions of Revit. It can work for either standalone computer or AVD image builder.

#### How to use
1. Go to working folder `L:\4b_Applied Computing\01_Revit\Initialization` prepare Revit.ini file for the target year version, make changes if needed (set default family template path to L drive, etc). Changes are to be confirmed by Gayatri. We will keep one Revit.ini file per folder because Revit separates them by folder. **Add install markup for any changes you want to add.**
2. Download https://github.com/Ennead-Architects-LLP/EA_Dist/blob/main/Installation/RevitIniDeployer.exe and run. This will try to find all years versions and copy to ProgramData version ini for each year.

### 8.3 EnscapeAssetChanger

This tool helps locate and modify Enscape material assets for visualization specialists who need precise control over their rendering assets.

#### What it does
- Search for Enscape assets by name using fuzzy search
- Browse and modify .matpkg material files for modern format assets
- Access texture files directly for legacy format assets
- Visual thumbnail preview of assets
- Material editor with color picker and property adjustment

#### How to use
1. Place Enscape assets in your Rhino model and start an Enscape scene to download the assets
2. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Apps`
3. Run `EnscapeAssetChanger.exe`
4. Use the search bar to find your assets
5. Click "Open Folder" to navigate to the asset location
6. For modern format assets: Edit .matpkg files with the built-in material editor
7. For legacy format assets: Edit texture images directly with external programs
8. Restart Rhino/Enscape to see changes take effect

#### Asset location
Assets are stored at: `C:\Users\[USERNAME]\AppData\Local\Temp\Enscape\Assets\Data`

### 8.4 LastSyncMonitor

This application monitors Revit file sync intervals and reminds users to sync their work regularly to prevent long periods without synchronization.

#### What it does
- Tracks time since last sync for all open Revit files
- Provides visual warnings when sync intervals exceed set thresholds
- Color-coded alerts: normal (white), warning (orange), critical (red)
- Automatic cost tracking for overtime periods
- Helps maintain good collaboration practices in shared Revit models

#### How to use
The monitor starts automatically when you open Revit files. The interface shows:
- Current sync status for all tracked documents
- Time elapsed since last sync
- Visual alerts when sync intervals become too long
- Default reminder interval is 45 minutes (configurable in EnneadTab settings)

#### Configuration
You can adjust the sync monitor interval in your EnneadTab Revit settings. The tool will remind you at the set interval and apply cost penalties for extended periods without syncing.

### 8.5 Pdf2indesign

This application converts PDF files into InDesign documents with professional layout options, perfect for design workflows that involve PDF-to-print conversions.

#### What it does
- Converts multi-page PDFs to properly formatted InDesign documents
- Two layout modes: Spread mode (one page per spread) and Booklet mode (two pages per spread)
- Automatic page dimension detection and scaling
- Customizable margins and measurement units (inches/millimeters)
- Media box or content box cropping options
- Batch processing support for multiple PDFs

#### How to use
1. Navigate to `C:\Users\[USER_NAME]\Documents\EnneadTab Ecosystem\EA_Dist\Apps`
2. Run `Pdf2indesign.exe`
3. Configure your settings:
   - InDesign version number
   - Page dimensions (width/height)
   - Margins (top, bottom, left, right)
   - Units (inches or millimeters)
   - Dimension type (Media Box or Content Box)
4. Choose layout mode:
   - **Spread mode**: Each PDF page becomes a full InDesign spread
   - **Booklet mode**: Portrait pages are placed side-by-side, landscape pages use full spreads
5. Select your PDF files for conversion
6. The tool will create .indd files in the same location as your PDFs

#### Supported workflow
- Ideal for converting consultant drawings or presentation materials to InDesign format
- Maintains proper scaling and proportions
- Automatically handles mixed portrait/landscape orientations in booklet mode
- Supports batch processing for efficient conversion of multiple documents
