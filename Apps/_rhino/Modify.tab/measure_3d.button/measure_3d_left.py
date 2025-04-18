__title__ = "Measure3D"
__doc__ = """Display 3D measurements between two points.

Shows total distance with a curve, and displays X, Y, Z differences as color-coded curves:
- X difference in red
- Y difference in green
- Z difference in blue

Measurements remain on screen until a new measurement is started.
"""

import Rhino # type: ignore
import scriptcontext as sc # type: ignore
import System # type: ignore

from EnneadTab import ERROR_HANDLE, LOG, SOUND
from EnneadTab.RHINO import RHINO_CONDUIT

MEASUREMENT_DISPLAY_KEY = "measure3d_display"

class MeasurementDisplay(RHINO_CONDUIT.RhinoConduit):
    """Display 3D measurements between points with colored components and labels."""
    
    def __init__(self):
        """Initialize measurement display conduit with default settings."""
        # Points and state
        self.start_point = None
        self.end_point = None
        self.preview_point = None  # Used for live preview during selection
        self.is_selecting_end_point = False
        
        # Display settings
        self.axis_colors = {
            "x": System.Drawing.Color.Red,
            "y": System.Drawing.Color.Green,
            "z": System.Drawing.Color.Blue
        }
        self.main_color = System.Drawing.Color.White
        self.point_label_size = 14
        self.distance_label_size = 15
        self.component_label_size = 12
        self.line_thickness = 2
        self.min_display_threshold = 0.001  # Don't show components smaller than this
    
    def reset(self):
        """Reset the measurement state."""
        self.start_point = None
        self.end_point = None
        self.preview_point = None
        self.is_selecting_end_point = False
    
    def set_start_point(self, point):
        """Set the start point for measurement."""
        self.start_point = Rhino.Geometry.Point3d(point)
        
    def set_end_point(self, point):
        """Set the end point for measurement."""
        self.end_point = Rhino.Geometry.Point3d(point)
        self.preview_point = None  # Clear preview once end point is set
    
    def set_selecting_end_point(self, is_selecting):
        """Set whether we're in the process of selecting the end point."""
        self.is_selecting_end_point = is_selecting
    
    def update_dynamic_point(self, point, is_start_point=False):
        """Update point during GetPoint operation."""
        if is_start_point:
            self.set_start_point(point)
        else:
            # During selection, update the preview point instead of end_point
            self.preview_point = Rhino.Geometry.Point3d(point)
        sc.doc.Views.Redraw()
    
    def calculate_differences(self, end_pt=None):
        """Calculate the component differences between points."""
        if not self.start_point:
            return None
            
        # Use provided end point, preview point, or end_point in that order
        end_point = end_pt if end_pt else (self.preview_point if self.preview_point else self.end_point)
        if not end_point:
            return None
            
        return {
            "x": end_point.X - self.start_point.X,
            "y": end_point.Y - self.start_point.Y,
            "z": end_point.Z - self.start_point.Z,
            "total": self.start_point.DistanceTo(end_point)
        }
    
    @RHINO_CONDUIT.try_catch_conduit_error
    def DrawForeground(self, e):
        """Draw measurement visualization in the viewport."""
        # Display start point if available
        if not self.start_point:
            return
            
        # Determine which point to use for end position (preview or final)
        end_point = None
        if self.is_selecting_end_point and self.preview_point:
            # Use preview during selection
            end_point = self.preview_point
        elif self.end_point:
            # Use final end point if set
            end_point = self.end_point
        
        # Draw the start point with appropriate label
        self._draw_labeled_point(e, self.start_point, 
                               "From Here" if self.is_selecting_end_point else "Start Pt")
        
        # If no end point available yet, nothing more to draw
        if not end_point:
            return
            
        # Draw end point
        self._draw_labeled_point(e, end_point, "To Here")
            
        # Calculate differences using the appropriate end point
        differences = self.calculate_differences(end_point)
        if not differences:
            return
            
        # Draw total distance line
        self._draw_total_distance(e, differences["total"], end_point)
        
        # Draw component differences
        self._draw_component_differences(e, differences, end_point)


        
    
    def _draw_labeled_point(self, e, point, label):
        """Draw a point with a text label."""
        e.Display.DrawDot(point, "")
        e.Display.Draw2dText(
            label,
            self.main_color,
            e.Viewport.WorldToClient(point),
            False,
            self.point_label_size
        )
    
    def _draw_total_distance(self, e, distance, end_point):
        """Draw the total distance line and label."""
        # Draw direct line between points
        line = Rhino.Geometry.Line(self.start_point, end_point)
        e.Display.DrawLine(line, self.main_color, self.line_thickness)
        
        # Draw midpoint text showing total distance
        midpoint = (self.start_point + end_point) / 2
        e.Display.DrawDot(midpoint, "")
        e.Display.Draw2dText(
            "{:.2f}".format(distance), 
            self.main_color, 
            e.Viewport.WorldToClient(midpoint),
            False, 
            self.distance_label_size
        )
    
    def _draw_component_differences(self, e, differences, end_point):
        """Draw the XYZ component differences."""
        # For X difference
        if abs(differences["x"]) > self.min_display_threshold:
            x_point = Rhino.Geometry.Point3d(
                end_point.X,
                self.start_point.Y,
                self.start_point.Z
            )
            x_line = Rhino.Geometry.Line(self.start_point, x_point)
            e.Display.DrawLine(x_line, self.axis_colors["x"], self.line_thickness)
            x_midpoint = (self.start_point + x_point) / 2
            e.Display.Draw2dText(
                "X: {:.2f}".format(differences["x"]), 
                self.axis_colors["x"], 
                e.Viewport.WorldToClient(x_midpoint),
                False, 
                self.component_label_size
            )
        
        # For Y difference
        if abs(differences["y"]) > self.min_display_threshold:
            if abs(differences["x"]) > self.min_display_threshold:
                # If X was drawn, start from there
                start_point = Rhino.Geometry.Point3d(
                    end_point.X,
                    self.start_point.Y,
                    self.start_point.Z
                )
            else:
                start_point = self.start_point
                
            y_point = Rhino.Geometry.Point3d(
                end_point.X,
                end_point.Y,
                self.start_point.Z
            )
            y_line = Rhino.Geometry.Line(start_point, y_point)
            e.Display.DrawLine(y_line, self.axis_colors["y"], self.line_thickness)
            y_midpoint = (start_point + y_point) / 2
            e.Display.Draw2dText(
                "Y: {:.2f}".format(differences["y"]), 
                self.axis_colors["y"], 
                e.Viewport.WorldToClient(y_midpoint),
                False, 
                self.component_label_size
            )
        
        # For Z difference
        if abs(differences["z"]) > self.min_display_threshold:
            if abs(differences["x"]) > self.min_display_threshold or abs(differences["y"]) > self.min_display_threshold:
                # If X or Y was drawn, start from there
                start_point = Rhino.Geometry.Point3d(
                    end_point.X,
                    end_point.Y,
                    self.start_point.Z
                )
            else:
                start_point = self.start_point
                
            z_line = Rhino.Geometry.Line(start_point, end_point)
            e.Display.DrawLine(z_line, self.axis_colors["z"], self.line_thickness)
            z_midpoint = (start_point + end_point) / 2
            e.Display.Draw2dText(
                "Z: {:.2f}".format(differences["z"]), 
                self.axis_colors["z"], 
                e.Viewport.WorldToClient(z_midpoint),
                False, 
                self.component_label_size
            )
    
    def print_measurement_results(self):
        """Print the measurement results to the command line."""
        differences = self.calculate_differences()
        if not differences:
            return
            
        print("Total distance: {:.2f}".format(differences["total"]))
        if abs(differences["x"]) > self.min_display_threshold:
            print("X difference: {:.2f}".format(differences["x"]))
        if abs(differences["y"]) > self.min_display_threshold:
            print("Y difference: {:.2f}".format(differences["y"]))
        if abs(differences["z"]) > self.min_display_threshold:
            print("Z difference: {:.2f}".format(differences["z"]))


class MeasureGetPoint(Rhino.Input.Custom.GetPoint):
    """Custom GetPoint class with enhanced dynamic draw capabilities."""
    
    def __init__(self, is_start_point=True):
        self.is_start_point = is_start_point
        
    def OnDynamicDraw(self, e):
        """Override the OnDynamicDraw event to update display constantly."""
        point = e.CurrentPoint
        
        # Call base class implementation
        Rhino.Input.Custom.GetPoint.OnDynamicDraw(self, e)
        
        # Update the display with current point
        if self.is_start_point:
            sc.sticky[MEASUREMENT_DISPLAY_KEY].update_dynamic_point(point, is_start_point=True)
        else:
            sc.sticky[MEASUREMENT_DISPLAY_KEY].update_dynamic_point(point, is_start_point=False)
            SOUND.play_sound("sound_effect_menu_tap")   
        
        # Force a redraw to show changes
        sc.doc.Views.Redraw()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def measure_3d():
    """Run 3D measurement tool with visual display conduit.
    
    Measurements remain visible until a new measurement is started,
    allowing camera rotation and navigation while viewing the measurements.
    """
    # Use sc.sticky for persistent storage between script runs
    if MEASUREMENT_DISPLAY_KEY not in sc.sticky:
        sc.sticky[MEASUREMENT_DISPLAY_KEY] = None
    
    # Clear previous display if it exists
    if sc.sticky[MEASUREMENT_DISPLAY_KEY]:
        sc.sticky[MEASUREMENT_DISPLAY_KEY].Enabled = False
        sc.doc.Views.Redraw()
    
    # Create new measurement display
    sc.sticky[MEASUREMENT_DISPLAY_KEY] = MeasurementDisplay()
    sc.sticky[MEASUREMENT_DISPLAY_KEY].Enabled = True
    
    # Get first point with custom GetPoint
    gp_start = MeasureGetPoint(is_start_point=True)
    gp_start.SetCommandPrompt("Select start point")
    result = gp_start.Get()
    
    if result != Rhino.Input.GetResult.Point:
        sc.sticky[MEASUREMENT_DISPLAY_KEY].Enabled = False
        return
    
    start_point = gp_start.Point()
    sc.sticky[MEASUREMENT_DISPLAY_KEY].set_start_point(start_point)
    
    # Update display to indicate we're selecting end point
    sc.sticky[MEASUREMENT_DISPLAY_KEY].set_selecting_end_point(True)
    
    # Get end point with custom GetPoint
    gp_end = MeasureGetPoint(is_start_point=False)
    gp_end.SetCommandPrompt("Select end point")
    gp_end.SetBasePoint(start_point, True)
    result = gp_end.Get()
    
    if result != Rhino.Input.GetResult.Point:
        sc.sticky[MEASUREMENT_DISPLAY_KEY].Enabled = False
        return
    
    end_point = gp_end.Point()
    sc.sticky[MEASUREMENT_DISPLAY_KEY].set_end_point(end_point)
    
    # Print measurement results
    sc.sticky[MEASUREMENT_DISPLAY_KEY].print_measurement_results()
    
    # Keep display visible until next measurement
    sc.doc.Views.Redraw()
    print("Measurement displayed. Start a new measurement to clear.")


def clear_measurements():
    """Clear the current measurement display."""
    if MEASUREMENT_DISPLAY_KEY in sc.sticky and sc.sticky[MEASUREMENT_DISPLAY_KEY]:
        sc.sticky[MEASUREMENT_DISPLAY_KEY].Enabled = False
        sc.sticky[MEASUREMENT_DISPLAY_KEY] = None
        sc.doc.Views.Redraw()


if __name__ == "__main__":
    measure_3d() 