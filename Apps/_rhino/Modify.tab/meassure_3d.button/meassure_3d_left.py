__title__ = "Meassure3D"
__doc__ = """Display 3D measurements between two points.

Shows total distance with a curve, and displays X, Y, Z differences as color-coded curves:
- X difference in red
- Y difference in green
- Z difference in blue

Measurements remain on screen until a new measurement is started.
"""

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.RHINO import RHINO_CONDUIT


class Measure3DConduit(RHINO_CONDUIT.RhinoConduit):
    
    def __init__(self):
        self.first_point = None
        self.second_point = None
        self.selecting_second_point = False
        self.x_color = System.Drawing.Color.Red
        self.y_color = System.Drawing.Color.Green
        self.z_color = System.Drawing.Color.Blue
        self.white = System.Drawing.Color.White
    
    @RHINO_CONDUIT.try_catch_conduit_error
    def DrawForeground(self, e):
        # Display first point if available
        if self.first_point:
            # Draw dot and label for first point
            e.Display.DrawDot(self.first_point, "")
            first_point_text = "From Here" if self.selecting_second_point else "Start Pt"
            e.Display.Draw2dText(
                first_point_text,
                self.white,
                e.Viewport.WorldToClient(self.first_point),
                False,
                14
            )
        
        # If only first point is available, nothing more to draw
        if not self.second_point:
            return
            
        # Draw dot and label for second point
        e.Display.DrawDot(self.second_point, "")
        e.Display.Draw2dText(
            "To Here",
            self.white,
            e.Viewport.WorldToClient(self.second_point),
            False,
            14
        )
            
        # Calculate differences
        dx = self.second_point.X - self.first_point.X
        dy = self.second_point.Y - self.first_point.Y
        dz = self.second_point.Z - self.first_point.Z
        
        # Calculate total distance
        total_distance = self.first_point.DistanceTo(self.second_point)
        
        # Draw direct line between points
        line = Rhino.Geometry.Line(self.first_point, self.second_point)
        e.Display.DrawLine(line, self.white, 2)
        
        # Draw midpoint text showing total distance
        midpoint = (self.first_point + self.second_point) / 2
        e.Display.DrawDot(midpoint, "")
        e.Display.Draw2dText(
            "{:.2f}".format(total_distance), 
            self.white, 
            e.Viewport.WorldToClient(midpoint),
            False, 
            15
        )
        
        # Draw component differences if they are not zero
        # For X difference
        if abs(dx) > 0.001:
            x_point = Rhino.Geometry.Point3d(
                self.second_point.X,
                self.first_point.Y,
                self.first_point.Z
            )
            x_line = Rhino.Geometry.Line(self.first_point, x_point)
            e.Display.DrawLine(x_line, self.x_color, 2)
            x_midpoint = (self.first_point + x_point) / 2
            e.Display.Draw2dText(
                "X: {:.2f}".format(dx), 
                self.x_color, 
                e.Viewport.WorldToClient(x_midpoint),
                False, 
                12
            )
        
        # For Y difference
        if abs(dy) > 0.001:
            if abs(dx) > 0.001:
                # If X was drawn, start from there
                start_point = Rhino.Geometry.Point3d(
                    self.second_point.X,
                    self.first_point.Y,
                    self.first_point.Z
                )
            else:
                start_point = self.first_point
                
            y_point = Rhino.Geometry.Point3d(
                self.second_point.X,
                self.second_point.Y,
                self.first_point.Z
            )
            y_line = Rhino.Geometry.Line(start_point, y_point)
            e.Display.DrawLine(y_line, self.y_color, 2)
            y_midpoint = (start_point + y_point) / 2
            e.Display.Draw2dText(
                "Y: {:.2f}".format(dy), 
                self.y_color, 
                e.Viewport.WorldToClient(y_midpoint),
                False, 
                12
            )
        
        # For Z difference
        if abs(dz) > 0.001:
            if abs(dx) > 0.001 or abs(dy) > 0.001:
                # If X or Y was drawn, start from there
                start_point = Rhino.Geometry.Point3d(
                    self.second_point.X,
                    self.second_point.Y,
                    self.first_point.Z
                )
            else:
                start_point = self.first_point
                
            z_line = Rhino.Geometry.Line(start_point, self.second_point)
            e.Display.DrawLine(z_line, self.z_color, 2)
            z_midpoint = (start_point + self.second_point) / 2
            e.Display.Draw2dText(
                "Z: {:.2f}".format(dz), 
                self.z_color, 
                e.Viewport.WorldToClient(z_midpoint),
                False, 
                12
            )


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def meassure_3d():
    """Run 3D measurement tool with visual display conduit.
    
    Measurements remain visible until a new measurement is started,
    allowing camera rotation and navigation while viewing the measurements.
    """
    # Use sc.sticky for persistent storage between script runs
    if "measure3d_conduit" not in sc.sticky:
        sc.sticky["measure3d_conduit"] = None
    
    # Clear previous conduit if it exists
    if sc.sticky["measure3d_conduit"]:
        sc.sticky["measure3d_conduit"].Enabled = False
        sc.doc.Views.Redraw()
    
    # Create conduit
    sc.sticky["measure3d_conduit"] = Measure3DConduit()
    sc.sticky["measure3d_conduit"].Enabled = True
    
    # Get first point with dot display
    gp1 = Rhino.Input.Custom.GetPoint()
    gp1.SetCommandPrompt("Select first point")
    gp1.DynamicDraw += lambda sender, args: dynamic_draw_first_point(sender, args, sc.sticky["measure3d_conduit"])
    gp1.Get()
    
    if gp1.CommandResult() != Rhino.Commands.Result.Success:
        sc.sticky["measure3d_conduit"].Enabled = False
        return
    
    first_point = gp1.Point()
    sc.sticky["measure3d_conduit"].first_point = Rhino.Geometry.Point3d(first_point)
    
    # Update conduit to indicate we're selecting second point
    sc.sticky["measure3d_conduit"].selecting_second_point = True
    
    # Get second point with dynamic display
    gp = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt("Select second point")
    gp.SetBasePoint(first_point, True)
    gp.DynamicDraw += lambda sender, args: dynamic_draw_callback(sender, args, sc.sticky["measure3d_conduit"])
    gp.Get()
    
    if gp.CommandResult() != Rhino.Commands.Result.Success:
        sc.sticky["measure3d_conduit"].Enabled = False
        return
    
    second_point = gp.Point()
    sc.sticky["measure3d_conduit"].second_point = Rhino.Geometry.Point3d(second_point)
    
    # Calculate results
    dx = second_point.X - first_point.X
    dy = second_point.Y - first_point.Y
    dz = second_point.Z - first_point.Z
    distance = first_point.DistanceTo(second_point)
    
    # Print results
    print("Total distance: {:.2f}".format(distance))
    if abs(dx) > 0.001:
        print("X difference: {:.2f}".format(dx))
    if abs(dy) > 0.001:
        print("Y difference: {:.2f}".format(dy))
    if abs(dz) > 0.001:
        print("Z difference: {:.2f}".format(dz))
    
    # Keep conduit visible until next measurement
    sc.doc.Views.Redraw()
    print("Measurement displayed. Start a new measurement to clear.")


def dynamic_draw_first_point(sender, args, conduit):
    """Update conduit during first point selection"""
    conduit.first_point = Rhino.Geometry.Point3d(args.CurrentPoint)
    sc.doc.Views.Redraw()


def dynamic_draw_callback(sender, args, conduit):
    """Update conduit during second point selection"""
    conduit.second_point = Rhino.Geometry.Point3d(args.CurrentPoint)
    sc.doc.Views.Redraw()


def clear_measurements():
    """Clear the current measurement display"""
    if "measure3d_conduit" in sc.sticky and sc.sticky["measure3d_conduit"]:
        sc.sticky["measure3d_conduit"].Enabled = False
        sc.sticky["measure3d_conduit"] = None
        sc.doc.Views.Redraw()


if __name__ == "__main__":
    meassure_3d()
