# EnneadTab for Revit
the repo is transferred from zsenarchitect to Ennead LLP on 2023-04-03

For any function request and bug report, please direct message Sen Zhang for help.



## The structure of this repo:

### ENNEAD.extension
* **Ennead.tab** - _core tab_
* **Ennead Library.tab** - _shared labeled content tab_
* **EnneadTab_Beta.tab** - _all remaining tools tab; this folder is not published to the stable version_
* **hooks** - _all basic hook files_
* **lib** - _all core modules_
  * EnneadTab - _Core module WIP; shared between EnneadTab for Revit and For Rhino_
  * EA_UTILITY.py - _previous core module, no longer edited other than to mark **""""""** in front of functions that have been migrated to new EnneadTab core module_
  * ENNEAD_LOG.py - _functions for checking mini bank; this will be migrated to core module in the future_
  * EA_startup.py - _auto run at revit startup; the most important usage is to register dockpane. This startup file will be simplified in the future._

### EnneadTab Developer.extension 
For code writer usage only. This extension is never exposed to beta testers.
* (((Ennead Alpha))).tab - _include script template and version control_
* EnneadTab Research.tab - _include good attempts to test different direction; not meant for production._

 

 


 
---
## Popular Functions:

1. **Sync Queue**
   * _Provide automatic manager solution to control multiple user sync traffic._
2. **Rhino2Revit**
   * _Geo Conversion: Provide easy use alternative to Rhino.Inside._
   * _Drafting Conversion: Take advantage of powerful drafting ability of Rhino._
3. **Tag Align**
   * _Provide easy solution to tedious manual workflow._
4. **Family Merge**
   * _Provide solution to manage family content while preserve graphical presentation._
5. **Exporter**
   * _A streamlined workflow for many commonly used submission preparation._
6. **Sync All**
   * _Provide easy relinquish solution at end of day for multiple project users._
7. **Toggle Content**
   * _Provide easy solution to tedious manual workflow on a number of fields._
8. **AI Translation** 
   * _Integrated translation solution for documentation._
9. **Dim Text**
   * _Provide easy solution to tedious manual workflow._
10. **View Name Rename**
    * _Increase readability to project browser._
11. **MiniBank**
    * _Gamification of work to encourage better practice._





<!-- topic below -->
how to install
tailor tab
Setting
search
Sync all and see you again
Renamer
toggle content
dwg manager
Dim helper
user keynote
tag aligner
merge family
AI translation
what happen
transfer content
fire rating graphic
family repath
load multiple family to multiple project
