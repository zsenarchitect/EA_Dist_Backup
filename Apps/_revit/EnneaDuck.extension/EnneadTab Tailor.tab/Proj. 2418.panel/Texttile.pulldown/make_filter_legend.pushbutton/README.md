# Make Filter Legend

## Overview
This tool creates filters for Generic Model family names, applies colors from a defined scheme, and generates a color legend that will be automatically placed on the current sheet.

## Features
- Define family names and colors in a simple CSS file
- Automatically creates view filters for each family name
- Generates a legend view with colored boxes and family names
- Places the legend on the current sheet
- Reuses existing filters and legend views when possible

## Usage
1. Define family names and colors in the `color_map.css` file
2. Open a view that is placed on a sheet (not a sheet view itself)
3. Run the "Make Filter Legend" tool
4. The tool will:
   - Read family definitions from the CSS file
   - Create or update filters for all defined families
   - Apply the colors specified in CSS
   - Create or update a legend view
   - Place the legend on the current sheet

## CSS Color Map
The tool reads family names and colors from a CSS file (`color_map.css`). This allows you to:
- Define exactly which families to include in the filters
- Specify precise colors for each family
- Control the appearance of your filter legend

### CSS Format
```css
/* Individual family colors */
.FamilyName1 {
    color: rgb(r, g, b);
}

.FamilyName2 {
    color: rgb(r, g, b);
}
```

Notes:
- Each family gets its own entry with a unique color
- Spaces in family names should be replaced with hyphens in the CSS
- The RGB color values should be 0-255 for each component
- If a family isn't defined in the CSS, it won't be included in the filters

### Example CSS
```css
/* Individual family colors */
.PanelA1 {
    color: rgb(255, 180, 25);  /* Light orange */
}

.PanelA2 {
    color: rgb(255, 195, 50);  /* Lighter orange */
}

.PanelB1 {
    color: rgb(30, 30, 255);  /* Light blue */
}
```

## Fallback Mode
If the CSS file doesn't exist or is empty, the tool will:
1. Scan the model for all Generic Model families
2. Group them by prefix pattern
3. Assign gradient colors automatically
4. Generate a new CSS file based on these families

## Requirements
- Revit 2020 or newer
- View must be placed on a sheet (not a sheet view) 