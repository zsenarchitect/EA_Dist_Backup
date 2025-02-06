> [!NOTE]
> Most of the tools mentioned below can be found in the tool panel. If needing help please ask Design Technology Team. Most of workflow of generating report and data can be customized by a tool somewhere in Design Technology Collection.


# NYU Health Design Guidelines



## Typical Design Phase Deliverables 🎨
<div style="border: 1px solid yellow; padding: 10px;">

| Category | SD (Sketchy Days) 🎭 | DD (Deep Dive) 🏊 | CD (Complete Details) 🎯 |
|----------|---------------------|-------------------|------------------------|
| **Demolition Plan** | ✓ | - | - |
| **Floor Plan** | w/FFE & notes | w/FFE, dimensions, partition tags, RED_F room #s | Fully coordinated |
| **Enlarged Floor Plan** | - | ✓ | ✓ |
| **Reflected Ceiling Plan** | - | ✓ | ✓ |
| **Elevations** | ✓ | ✓ | ✓ |
| **Sections** | - | ✓ | ✓ |
| **Schedules** | - | Room Finishes, Furniture, Door, Door Hardware, Lighting, Pubing Fixture, Toilet Axcessory | DD level |
| **Details** | - | Typical and Major only | All details |
| **Renderings** | ✓ | ✓ | ✓ |
| **Specs Material** | Outline | Updated | Final |
| **Finish and Furniture Booklets** | - | Outline | Final |
| **Equipment List** | Outline | Updated | Final |
| **Architect and Engineering Specs** | outline | Updated | Final |
</div>

<br>
<br>
<br>
<br>

## 1. Project Info Setup Requirements


### 1.1. Essential Project Info Parameters
    - ParaName: PIM
    - ParaType: Text
    - Description: Project Identification Number(PIM#) for NYU Health Project
    - HandledByEnneadTabSetup: Yes
    
    - ParaName: EnneadTab_Data
    - ParaType: Text
    - Description: (Optional)Name of the json file that stores all the customize data for the project.
    - HandledByEnneadTabSetup: Yes







### 1.2. Linked View Setup
> [!NOTE]
> Work In Progress

Use linked view setup tool to set cross discipline background view.


### 1.3. Material Setting
Use material setting tool to set material for project.

### 1.4. Container File Checker



## 2. Area Tracking


### 2.1 General Workflow


### Required Area Schemes
- **"GFA Scheme"** [Area Scheme] 
  - Tracing of outline on each level
  - Single area per level

- **"DGSF Scheme"** [Area Scheme]
  - SD stage: Area separation lines
  - DD stage: Walls as bounding elements
### Concept and SD Phase
- Use rooms for area calculations
- Use room separation lines as bounding elements
- **Important Note on Design Options:** 

  - Avoid using design options for total massing studies (e.g., T building vs L building)
  - Instead, duplicate the entire model for new schemes
  - Risk warning: Design options can be tricky. If one person is editing a design option then him/her own the entire set. Using area scheme means parrlel editing. To duplicate a scheme setup without recreating all the area bounary and area, see Sen for help.

### DD Phase and Later
- Switch to walls as bounding elements

### 2.2 Department and Program Color Scheme updater

### 2.3 DGSF Chart Updater

### 2.4 Department and Program Name Checker


## 3. Patient Bed Calculation
### 3.1 Setup
### 3.2 Workflow

## 4. Parking Calculation
### 4.1 Setup
### 4.2 Workflow


## 5. Room Data Sheet
### 5.1 Setup
### 5.2 Workflow


## 6. Life Safety Calculation
### 6.1 Setup
### 6.2 Workflow




## 7. Essential Families
### 7.1 System Families
WallType data matcher

### 7.2 Furniture Families
- Elevator
- Elevator door
- Parking stall
- Parking Tag
- Patient bed room planner


## 8. Exporting

### 8.1 Sheet List Organization

    A-000 General Information
    A-100 Floor Plans
    A-200 Elevations
    A-300 Exterial Detrails
    A-400 Interior Detrails
    A-500 Vertical Transportation
    A-600 Reflected Ceiling Plans
    A-700 Finish Plans
    A-800 Schedules

Sheet Setup:

### 8.2 Exporting DWG
<div style="border: 1px solid yellow; padding: 10px;">
#### CAD Layer Standards 🎨

| Category | REDI-F Layer Name | Description | Color | Lineweight | Linetype |

|----------|------------------|-------------|--------|------------|----------|
| Architectural | A-CURB | Curbs for Equipment | 2-yellow | Default | Continuous |
| Architectural | A-DOOR | Doors | 1-red | Default | Continuous |
| Architectural | A-DOOR-DEN | Door number, hardware group, etc. | 4-cyan | Default | Continuous |
| Architectural | A-FLOR-EVTR | Elevator cars and equipment | 2-yellow | Default | Continuous |
| Architectural | A-FLOR-GRATE | Grating | 2-yellow | Default | Continuous |
| Architectural | A-FLOR-DEN-ROOM | Room numbers | 7-white | Default | Continuous |
| Architectural | A-FLOR-DEN-PRE-EPC | Pre-EPC Room numbers | 7-white | Default | Continuous |
| Architectural | A-FLOR-DEN-TEXT | Room names, target, comments, etc. | 7-white | Default | Continuous |
| Architectural | A-FLOR-SHFT | Shafts | 2-yellow | Default | Continuous |
| Architectural | A-FLOR-SIGN | Signage | 1-red | Default | Continuous |
| Architectural | A-FLOR-STRS | Stair treads, escalators, ladders, level changes, ramps, etc. depressions | 2-yellow | Default | Continuous |
| Architectural | A-ROOF | Roof | 1-red | Default | Continuous |
| Architectural | A-WALL-EXTR | Exterior Building Wall | 5-blue | Default | Continuous |
| Architectural | A-WALL-INTR | Interior Building Wall | 3-green | Default | Continuous |
| Architectural | A-WNDW | Windows, curtain walls, glazed partitions | 4-cyan | Default | Continuous |
| General | DEFPOINTS | Defpoints | 7-white | Default | Continuous |
| Electrical | E-LITE | Lighting | 3-green | Default | Continuous |
| Electrical | E-LITE-EXIT | Exit lighting | 3-green | Default | Continuous |
| Electrical | E-POWR-WALL | Power wall outlets and receptacles | 3-green | Default | Continuous |
| Electrical | E-SAFETY-CRDNR | Card reader | 3-green | Default | Continuous |
| Electrical | E-SAFETY-ICBS | Intercom/door buzzer system | 3-green | Default | Continuous |
| Electrical | E-SYMB | Symbols | 3-green | Default | Continuous |
| General | G-ANNO-TEXT | General Text | 7-white | Default | Continuous |
| General | G-ANNO-TTLB | Border and Title Block | 7-white | Default | Continuous |
| General | G-ANNO-TTLB-TEXT | Border and Title Block Text | 7-white | Default | Continuous |
| General | G-LOGO | Title Block Logo | 94,56,150 | Default | Continuous |
| General | G-SCALE | Scale | 7-white | Default | Continuous |
| General | G-VP | Viewport | 7-white | Default | Continuous |
| Interior | I-EQPM-FIX | Fixed Equipment, except HVAC | 6-magenta | Default | Continuous |
| Interior | I-EQPM-MOV | Moveable equipment | 6-magenta | Default | Continuous |
| Interior | I-FURN | Furniture | 6-magenta | Default | Continuous |
| Interior | I-CASE | Cabinetry / Casement | 6-magenta | Default | Continuous |
| Landscaping | L-SITE | Site improvements | 4-cyan | Default | Continuous |
| Mechanical | M-HVAC-EQPM | Mechanical equip. (chiller, boiler etc.) | 6-magenta | Default | Continuous |
| Plumbing | P-FIXT | Plumbing fixtures, bowls, sinks | 6-magenta | Default | Continuous |
| Plumbing | P-SAFETY-SWSH | Emergency shower and eye wash | 2-yellow | Default | Continuous |
| Structural | S-COLS | Columns | 2-yellow | Default | Center |
| Structural | S-GRID | Column grid | 2-yellow | Default | Center |
| Telecomm | T-JACK | Data/telephone jacks | 3-green | Default | Continuous |
</div>

- CAD Layer Mapping Check tool
- File name format tool

Desired Format:

    PIM#-SheetName-SheetName.dwg
    Example:

    10662-A-101_First Floor Plan.dwg


### 8.3 Exporting PDF
- File exportor

Desired Format:
    PIM#-SheetName-SheetName.pdf
    Example:
    10662-A-101_First Floor Plan.pdf

### 8.4 Exporting Rhino
- layer name mapping tool
- workflow:
    - Isolated System exporter
    - Revit2Rhino


### 8.5 Exporting Revit
Desired Format:

    PIM#-Discipline.rvt
    Example:
    10662-A.rvt


## 9. Material Specific Generator
generate formated specfic doc based on revit family type image



<br>
<br>

## See below for snippets from NYU Guide.pdf

