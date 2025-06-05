"""
Rhino.Inside.Cpython Generation Functions Collection
15 Interesting and Fun Generation Functions for Parametric Design and Computational Geometry

This script demonstrates various capabilities of Rhino.Inside.Cpython for:
- Parametric modeling
- Generative art
- Computational geometry
- Nature-inspired forms
- Mathematical visualizations
- Architectural elements
"""

import rhinoinside
rhinoinside.load()

import System
import Rhino
import Rhino.Geometry as rg
import math
import random
import os

# Initialize Rhino document
doc = Rhino.RhinoDoc.CreateHeadless(None)

def clear_document():
    """Clear all objects from the document"""
    doc.Objects.Clear()

def save_and_open_file(filename):
    """Save the current document and add to files to open"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    rhino_auto_folder = os.path.join(desktop_path, "RhinoAuto")
    
    # Create RhinoAuto folder if it doesn't exist
    if not os.path.exists(rhino_auto_folder):
        os.makedirs(rhino_auto_folder)
    
    file_path = os.path.join(rhino_auto_folder, f"{filename}.3dm")
    
    try:
        # Write the current document directly
        doc.WriteFile(file_path, None)
        return file_path
    except:
        # Alternative approach - create simple 3dm file with object data
        try:
            import Rhino.FileIO as rf
            file3dm = rf.File3dm()
            
            # Add all objects to the file
            for obj in doc.Objects:
                if obj.Geometry:
                    # Create object attributes
                    attrs = Rhino.DocObjects.ObjectAttributes()
                    # Add based on geometry type
                    if isinstance(obj.Geometry, rg.Brep):
                        file3dm.Objects.AddBrep(obj.Geometry, attrs)
                    elif isinstance(obj.Geometry, rg.Mesh):
                        file3dm.Objects.AddMesh(obj.Geometry, attrs)
                    elif isinstance(obj.Geometry, rg.Curve):
                        file3dm.Objects.AddCurve(obj.Geometry, attrs)
                    elif isinstance(obj.Geometry, rg.NurbsCurve):
                        file3dm.Objects.AddCurve(obj.Geometry, attrs)
            
            # Write the file
            file3dm.Write(file_path, 7)  # Write as Rhino 7 format
            return file_path
        except Exception as e:
            print(f"     Warning: Could not save {filename}: {str(e)}")
            return None

# =====================================================================
# GENERATION FUNCTION 1: FIBONACCI SPIRAL TOWER
# =====================================================================
def generate_fibonacci_spiral_tower():
    """Generate a tower based on Fibonacci spiral with varying radii"""
    clear_document()
    
    fibonacci_numbers = [1, 1]
    for i in range(2, 20):
        fibonacci_numbers.append(fibonacci_numbers[i-1] + fibonacci_numbers[i-2])
    
    center = rg.Point3d(0, 0, 0)
    
    for i, fib_num in enumerate(fibonacci_numbers):
        angle = i * 137.5 * math.pi / 180  # Golden angle
        radius = fib_num * 0.5
        height = i * 2
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        circle_center = rg.Point3d(x, y, height)
        
        circle = rg.Circle(circle_center, fib_num * 0.3)
        cylinder = rg.Cylinder(circle, 1.5)
        brep = cylinder.ToBrep(True, True)
        
        doc.Objects.AddBrep(brep)
    
    print("Generated Fibonacci Spiral Tower!")

# =====================================================================
# GENERATION FUNCTION 2: VORONOI CITYSCAPE
# =====================================================================
def generate_voronoi_cityscape():
    """Generate a cityscape using Voronoi patterns for building placement"""
    clear_document()
    
    # Generate random seed points
    seed_points = []
    for i in range(50):
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        seed_points.append(rg.Point3d(x, y, 0))
    
    # Create buildings at each seed point
    for point in seed_points:
        width = random.uniform(2, 8)
        depth = random.uniform(2, 8)
        height = random.uniform(5, 30)
        
        # Create building base
        corner1 = rg.Point3d(point.X - width/2, point.Y - depth/2, 0)
        corner2 = rg.Point3d(point.X + width/2, point.Y + depth/2, height)
        
        box = rg.Box(rg.BoundingBox(corner1, corner2))
        building = box.ToBrep()
        
        doc.Objects.AddBrep(building)
    
    print("Generated Voronoi Cityscape!")

# =====================================================================
# GENERATION FUNCTION 3: PARAMETRIC WAVE SURFACE
# =====================================================================
def generate_parametric_wave_surface():
    """Generate a complex wave surface using mathematical functions"""
    clear_document()
    
    # Create mesh instead of NURBS surface for better compatibility
    mesh = rg.Mesh()
    
    # Generate vertices
    for u in range(0, 51, 2):
        for v in range(0, 51, 2):
            x = u * 0.5
            y = v * 0.5
            z = 5 * math.sin(x * 0.2) * math.cos(y * 0.2) + 2 * math.sin(x * 0.5) * math.sin(y * 0.3)
            mesh.Vertices.Add(rg.Point3d(x, y, z))
    
    # Create faces
    cols = 26  # (51//2 + 1)
    rows = 26
    
    for i in range(rows - 1):
        for j in range(cols - 1):
            v0 = i * cols + j
            v1 = i * cols + (j + 1)
            v2 = (i + 1) * cols + (j + 1)
            v3 = (i + 1) * cols + j
            
            mesh.Faces.AddFace(v0, v1, v2, v3)
    
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    
    doc.Objects.AddMesh(mesh)
    
    print("Generated Parametric Wave Surface!")

# =====================================================================
# GENERATION FUNCTION 4: FRACTAL TREE GENERATOR
# =====================================================================
def generate_fractal_tree():
    """Generate a 3D fractal tree using recursive branching"""
    clear_document()
    
    def create_branch(start_point, direction, length, depth, angle_variation):
        if depth <= 0 or length < 0.5:
            return
        
        # Calculate end point
        end_point = start_point + direction * length
        
        # Create branch cylinder
        branch_radius = length * 0.05
        circle = rg.Circle(start_point, branch_radius)
        
        # Create cylinder with proper height vector
        height_vector = rg.Vector3d(end_point - start_point)
        cylinder = rg.Cylinder(circle, height_vector.Length)
        
        # Transform cylinder to correct orientation
        brep = cylinder.ToBrep(True, True)
        
        # Create transformation to align cylinder
        if height_vector.Length > 0:
            height_vector.Unitize()
            z_axis = rg.Vector3d.ZAxis
            rotation = rg.Transform.Rotation(z_axis, height_vector, start_point)
            brep.Transform(rotation)
        
        doc.Objects.AddBrep(brep)
        
        # Create child branches
        num_branches = random.randint(2, 4)
        for i in range(num_branches):
            # Random rotation around Z axis
            rotation_angle = random.uniform(-angle_variation, angle_variation)
            bend_angle = random.uniform(-30, 30) * math.pi / 180
            
            # Create new direction
            new_direction = rg.Vector3d(direction)
            new_direction.Rotate(rotation_angle * math.pi / 180, rg.Vector3d.ZAxis)
            
            # Cross product for bend rotation
            cross = rg.Vector3d.CrossProduct(new_direction, rg.Vector3d.ZAxis)
            if cross.Length > 0:
                cross.Unitize()
                new_direction.Rotate(bend_angle, cross)
            
            # Recursive call
            new_length = length * random.uniform(0.6, 0.8)
            create_branch(end_point, new_direction, new_length, depth - 1, angle_variation * 1.2)
    
    # Start the tree
    start_point = rg.Point3d(0, 0, 0)
    initial_direction = rg.Vector3d(0, 0, 1)
    create_branch(start_point, initial_direction, 10, 6, 45)
    
    print("Generated Fractal Tree!")

# =====================================================================
# GENERATION FUNCTION 5: GEODESIC DOME VARIATIONS
# =====================================================================
def generate_geodesic_dome_variations():
    """Generate multiple geodesic dome variations"""
    clear_document()
    
    def create_geodesic_dome(center, radius, frequency):
        # Create icosahedron base
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        
        vertices = [
            rg.Point3d(-1, phi, 0), rg.Point3d(1, phi, 0), rg.Point3d(-1, -phi, 0), rg.Point3d(1, -phi, 0),
            rg.Point3d(0, -1, phi), rg.Point3d(0, 1, phi), rg.Point3d(0, -1, -phi), rg.Point3d(0, 1, -phi),
            rg.Point3d(phi, 0, -1), rg.Point3d(phi, 0, 1), rg.Point3d(-phi, 0, -1), rg.Point3d(-phi, 0, 1)
        ]
        
        # Normalize and scale vertices
        normalized_vertices = []
        for v in vertices:
            # Calculate vector from origin
            vector = rg.Vector3d(v.X, v.Y, v.Z)
            vector.Unitize()
            normalized_point = center + vector * radius
            normalized_vertices.append(normalized_point)
        
        # Create sphere at each vertex
        for vertex in normalized_vertices:
            sphere = rg.Sphere(vertex, radius * 0.05)
            brep = sphere.ToBrep()
            doc.Objects.AddBrep(brep)
    
    # Create multiple domes
    positions = [
        rg.Point3d(0, 0, 0),
        rg.Point3d(25, 0, 0),
        rg.Point3d(-25, 0, 0),
        rg.Point3d(0, 25, 0),
        rg.Point3d(0, -25, 0)
    ]
    
    for i, pos in enumerate(positions):
        create_geodesic_dome(pos, 8 + i * 2, i + 1)
    
    print("Generated Geodesic Dome Variations!")

# =====================================================================
# GENERATION FUNCTION 6: LISSAJOUS CURVES IN 3D
# =====================================================================
def generate_lissajous_curves_3d():
    """Generate 3D Lissajous curves with varying parameters"""
    clear_document()
    
    def create_lissajous_curve(a, b, c, delta_x, delta_y, delta_z, scale, offset):
        points = []
        for t in range(0, 1000):
            t_rad = t * 2 * math.pi / 100
            
            x = scale * math.sin(a * t_rad + delta_x) + offset.X
            y = scale * math.sin(b * t_rad + delta_y) + offset.Y
            z = scale * math.sin(c * t_rad + delta_z) + offset.Z
            
            points.append(rg.Point3d(x, y, z))
        
        # Create NURBS curve 
        if len(points) > 1:
            # Convert to Point3d array
            point_array = System.Array[rg.Point3d](points)
            curve = rg.Curve.CreateInterpolatedCurve(point_array, 3)
            if curve:
                doc.Objects.AddCurve(curve)
    
    # Generate multiple Lissajous curves
    configurations = [
        (3, 2, 1, 0, math.pi/2, 0, 10, rg.Point3d(0, 0, 0)),
        (5, 3, 2, math.pi/4, 0, math.pi/3, 8, rg.Point3d(30, 0, 0)),
        (4, 3, 5, 0, math.pi/3, math.pi/6, 6, rg.Point3d(-30, 0, 0)),
        (7, 5, 3, math.pi/6, math.pi/4, math.pi/2, 4, rg.Point3d(0, 30, 0)),
    ]
    
    for config in configurations:
        create_lissajous_curve(*config)
    
    print("Generated 3D Lissajous Curves!")

# =====================================================================
# GENERATION FUNCTION 7: CELLULAR AUTOMATA STRUCTURES
# =====================================================================
def generate_cellular_automata_structures():
    """Generate 3D structures based on cellular automata rules"""
    clear_document()
    
    def apply_rule(neighbors):
        """Simple rule: cell survives if it has 2-3 neighbors"""
        alive_count = sum(neighbors)
        return 1 if alive_count in [2, 3] else 0
    
    # Initialize 3D grid
    size = 20
    grid = [[[random.randint(0, 1) for _ in range(size)] for _ in range(size)] for _ in range(size)]
    
    # Apply cellular automata rules for a few iterations
    for iteration in range(3):
        new_grid = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
        
        for x in range(1, size-1):
            for y in range(1, size-1):
                for z in range(1, size-1):
                    # Count neighbors
                    neighbors = []
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            for dz in [-1, 0, 1]:
                                if dx == 0 and dy == 0 and dz == 0:
                                    continue
                                neighbors.append(grid[x+dx][y+dy][z+dz])
                    
                    new_grid[x][y][z] = apply_rule(neighbors)
        
        grid = new_grid
    
    # Create geometry for alive cells
    for x in range(size):
        for y in range(size):
            for z in range(size):
                if grid[x][y][z] == 1:
                    center = rg.Point3d(x, y, z)
                    sphere = rg.Sphere(center, 0.4)
                    brep = sphere.ToBrep()
                    doc.Objects.AddBrep(brep)
    
    print("Generated Cellular Automata Structures!")

# =====================================================================
# GENERATION FUNCTION 8: TWISTED SPIRE COLLECTION
# =====================================================================
def generate_twisted_spire_collection():
    """Generate a collection of twisted spires with varying parameters"""
    clear_document()
    
    def create_twisted_spire(base_center, base_radius, height, twist_angle, sides):
        # Create base profile
        points = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            x = base_center.X + base_radius * math.cos(angle)
            y = base_center.Y + base_radius * math.sin(angle)
            points.append(rg.Point3d(x, y, base_center.Z))
        
        points.append(points[0])  # Close the curve
        point_array = System.Array[rg.Point3d](points)
        base_curve = rg.Curve.CreateInterpolatedCurve(point_array, 3)
        
        # Create top profile (smaller and twisted)
        top_points = []
        top_radius = base_radius * 0.1
        for i in range(sides):
            angle = 2 * math.pi * i / sides + twist_angle
            x = base_center.X + top_radius * math.cos(angle)
            y = base_center.Y + top_radius * math.sin(angle)
            top_points.append(rg.Point3d(x, y, base_center.Z + height))
        
        top_points.append(top_points[0])
        top_point_array = System.Array[rg.Point3d](top_points)
        top_curve = rg.Curve.CreateInterpolatedCurve(top_point_array, 3)
        
        # Create loft
        curve_array = System.Array[rg.Curve]([base_curve, top_curve])
        loft = rg.Brep.CreateFromLoft(curve_array, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
        
        if loft and len(loft) > 0:
            doc.Objects.AddBrep(loft[0])
    
    # Generate multiple spires
    positions = [
        (rg.Point3d(0, 0, 0), 4, 20, math.pi, 6),
        (rg.Point3d(15, 0, 0), 3, 25, math.pi * 1.5, 8),
        (rg.Point3d(-15, 0, 0), 5, 18, math.pi * 0.5, 5),
        (rg.Point3d(0, 15, 0), 2.5, 30, math.pi * 2, 12),
        (rg.Point3d(0, -15, 0), 3.5, 22, math.pi * 0.75, 7),
    ]
    
    for pos, radius, height, twist, sides in positions:
        create_twisted_spire(pos, radius, height, twist, sides)
    
    print("Generated Twisted Spire Collection!")

# =====================================================================
# GENERATION FUNCTION 9: PARAMETRIC CORAL REEF
# =====================================================================
def generate_parametric_coral_reef():
    """Generate organic coral-like structures"""
    clear_document()
    
    def create_coral_branch(start_point, direction, radius, length, depth):
        if depth <= 0 or radius < 0.2:
            return
        
        # Create main branch
        end_point = start_point + direction * length
        
        # Create varying radius along the branch
        sections = 10
        for i in range(sections):
            t = i / float(sections - 1)
            current_radius = radius * (1 - t * 0.3)  # Taper
            section_point = start_point + direction * (length * t)
            
            sphere = rg.Sphere(section_point, current_radius)
            brep = sphere.ToBrep()
            doc.Objects.AddBrep(brep)
        
        # Create sub-branches
        num_branches = random.randint(2, 5)
        for i in range(num_branches):
            branch_start = start_point + direction * (length * random.uniform(0.3, 0.8))
            
            # Random direction with some upward bias
            angle_xy = random.uniform(0, 2 * math.pi)
            angle_z = random.uniform(-math.pi/6, math.pi/3)
            
            new_direction = rg.Vector3d(
                math.cos(angle_xy) * math.cos(angle_z),
                math.sin(angle_xy) * math.cos(angle_z),
                math.sin(angle_z)
            )
            
            new_radius = radius * random.uniform(0.5, 0.8)
            new_length = length * random.uniform(0.6, 0.9)
            
            create_coral_branch(branch_start, new_direction, new_radius, new_length, depth - 1)
    
    # Create multiple coral colonies
    base_points = [
        rg.Point3d(0, 0, 0),
        rg.Point3d(15, 5, 0),
        rg.Point3d(-10, 8, 0),
        rg.Point3d(8, -12, 0),
        rg.Point3d(-15, -5, 0),
    ]
    
    for base_point in base_points:
        initial_direction = rg.Vector3d(0, 0, 1)
        create_coral_branch(base_point, initial_direction, 2, 8, 4)
    
    print("Generated Parametric Coral Reef!")

# =====================================================================
# GENERATION FUNCTION 10: HYPERBOLIC PARABOLOID PAVILION
# =====================================================================
def generate_hyperbolic_paraboloid_pavilion():
    """Generate architectural pavilion using hyperbolic paraboloid surfaces"""
    clear_document()
    
    def create_hypar_surface(corner1, corner2, corner3, corner4):
        # Create control points for hyperbolic paraboloid using mesh
        mesh = rg.Mesh()
        
        # Add vertices
        mesh.Vertices.Add(corner1)
        mesh.Vertices.Add(corner2)
        mesh.Vertices.Add(corner3)
        mesh.Vertices.Add(corner4)
        
        # Create face
        mesh.Faces.AddFace(0, 1, 3, 2)
        
        mesh.Normals.ComputeNormals()
        doc.Objects.AddMesh(mesh)
    
    # Create multiple connected hypar surfaces
    base_size = 15
    height_variation = 8
    
    # Grid of hypar surfaces
    for i in range(3):
        for j in range(3):
            x_base = i * base_size
            y_base = j * base_size
            
            # Corner heights with some variation
            h1 = random.uniform(0, height_variation)
            h2 = random.uniform(0, height_variation)
            h3 = random.uniform(0, height_variation)
            h4 = random.uniform(0, height_variation)
            
            corner1 = rg.Point3d(x_base, y_base, h1)
            corner2 = rg.Point3d(x_base + base_size, y_base, h2)
            corner3 = rg.Point3d(x_base, y_base + base_size, h3)
            corner4 = rg.Point3d(x_base + base_size, y_base + base_size, h4)
            
            create_hypar_surface(corner1, corner2, corner3, corner4)
    
    print("Generated Hyperbolic Paraboloid Pavilion!")

# =====================================================================
# GENERATION FUNCTION 11: PARTICLE SYSTEM CONSTELLATION
# =====================================================================
def generate_particle_system_constellation():
    """Generate a 3D constellation using particle system simulation"""
    clear_document()
    
    class Particle:
        def __init__(self, position, velocity, size):
            self.position = position
            self.velocity = velocity
            self.size = size
            self.trail = [rg.Point3d(position)]
    
    # Initialize particles
    particles = []
    for i in range(100):
        pos = rg.Point3d(
            random.uniform(-20, 20),
            random.uniform(-20, 20),
            random.uniform(-20, 20)
        )
        vel = rg.Vector3d(
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5)
        )
        size = random.uniform(0.1, 0.5)
        particles.append(Particle(pos, vel, size))
    
    # Simulate particle movement
    for step in range(50):
        for particle in particles:
            # Update position
            particle.position = particle.position + particle.velocity
            particle.trail.append(rg.Point3d(particle.position))
            
            # Add some gravitational effect toward center
            center_force = rg.Vector3d(0, 0, 0) - rg.Vector3d(particle.position)
            center_force.Unitize()
            center_force = center_force * 0.01
            particle.velocity = particle.velocity + center_force
            
            # Limit trail length
            if len(particle.trail) > 20:
                particle.trail.pop(0)
    
    # Create geometry
    for particle in particles:
        # Create sphere at final position
        sphere = rg.Sphere(particle.position, particle.size)
        brep = sphere.ToBrep()
        doc.Objects.AddBrep(brep)
        
        # Create trail curve
        if len(particle.trail) > 2:
            trail_array = System.Array[rg.Point3d](particle.trail)
            trail_curve = rg.Curve.CreateInterpolatedCurve(trail_array, 3)
            if trail_curve:
                doc.Objects.AddCurve(trail_curve)
    
    print("Generated Particle System Constellation!")

# =====================================================================
# GENERATION FUNCTION 12: TENSEGRITY STRUCTURE NETWORK
# =====================================================================
def generate_tensegrity_structure_network():
    """Generate tensegrity-inspired structural networks"""
    clear_document()
    
    def create_tensegrity_unit(center, size):
        # Create compression members (solid rods)
        vertices = [
            center + rg.Vector3d(size, 0, 0),
            center + rg.Vector3d(-size/2, size*0.866, 0),
            center + rg.Vector3d(-size/2, -size*0.866, 0),
            center + rg.Vector3d(0, 0, size*1.5)
        ]
        
        # Compression members - using simple line representations
        for i in range(3):
            start = vertices[i]
            end = vertices[3]
            
            # Create line
            line = rg.Line(start, end)
            doc.Objects.AddCurve(line.ToNurbsCurve())
        
        # Tension members (cables - represented as lines)
        for i in range(3):
            for j in range(i+1, 3):
                line = rg.Line(vertices[i], vertices[j])
                doc.Objects.AddCurve(line.ToNurbsCurve())
    
    # Create network of tensegrity units
    spacing = 8
    for x in range(-2, 3):
        for y in range(-2, 3):
            for z in range(0, 3):
                center = rg.Point3d(x * spacing, y * spacing, z * spacing)
                size = 2 + z * 0.5
                create_tensegrity_unit(center, size)
    
    print("Generated Tensegrity Structure Network!")

# =====================================================================
# GENERATION FUNCTION 13: ALGORITHMIC FLOWER GARDEN
# =====================================================================
def generate_algorithmic_flower_garden():
    """Generate a garden of algorithmic flowers using mathematical patterns"""
    clear_document()
    
    def create_flower(center, petal_count, petal_size, stem_height):
        # Create stem as a line
        stem_start = center
        stem_end = center + rg.Vector3d(0, 0, stem_height)
        stem_line = rg.Line(stem_start, stem_end)
        doc.Objects.AddCurve(stem_line.ToNurbsCurve())
        
        # Create petals as circles
        flower_center = stem_end
        for i in range(petal_count):
            angle = 2 * math.pi * i / petal_count
            
            # Petal position
            petal_center = flower_center + rg.Vector3d(
                petal_size * 0.5 * math.cos(angle),
                petal_size * 0.5 * math.sin(angle),
                0
            )
            
            # Create petal as circle
            circle = rg.Circle(petal_center, petal_size * 0.3)
            doc.Objects.AddCurve(circle.ToNurbsCurve())
        
        # Create flower center
        center_sphere = rg.Sphere(flower_center, petal_size * 0.2)
        center_brep = center_sphere.ToBrep()
        doc.Objects.AddBrep(center_brep)
    
    # Create garden layout
    flower_positions = []
    for i in range(25):
        x = random.uniform(-20, 20)
        y = random.uniform(-20, 20)
        flower_positions.append(rg.Point3d(x, y, 0))
    
    # Generate flowers
    for pos in flower_positions:
        petal_count = random.randint(5, 12)
        petal_size = random.uniform(1, 3)
        stem_height = random.uniform(3, 8)
        create_flower(pos, petal_count, petal_size, stem_height)
    
    print("Generated Algorithmic Flower Garden!")

# =====================================================================
# GENERATION FUNCTION 14: MORPHING MESH LANDSCAPE
# =====================================================================
def generate_morphing_mesh_landscape():
    """Generate a complex landscape using mesh morphing techniques"""
    clear_document()
    
    # Create base mesh grid
    width, height = 50, 50
    resolution = 2
    
    vertices = []
    faces = []
    
    # Generate vertices with procedural height
    for i in range(0, width + 1, resolution):
        for j in range(0, height + 1, resolution):
            x = i - width / 2
            y = j - height / 2
            
            # Complex height function combining multiple sine waves
            z = (5 * math.sin(x * 0.2) * math.cos(y * 0.15) +
                 3 * math.sin(x * 0.4) * math.sin(y * 0.3) +
                 2 * math.sin(x * 0.8) * math.cos(y * 0.6) +
                 math.sin(x * 1.2) * math.sin(y * 1.1))
            
            vertices.append(rg.Point3d(x, y, z))
    
    # Create faces
    rows = (width // resolution) + 1
    cols = (height // resolution) + 1
    
    for i in range(rows - 1):
        for j in range(cols - 1):
            # Current quad vertices
            v0 = i * cols + j
            v1 = i * cols + (j + 1)
            v2 = (i + 1) * cols + (j + 1)
            v3 = (i + 1) * cols + j
            
            # Create two triangular faces
            faces.append(rg.MeshFace(v0, v1, v2))
            faces.append(rg.MeshFace(v0, v2, v3))
    
    # Create mesh
    mesh = rg.Mesh()
    for vertex in vertices:
        mesh.Vertices.Add(vertex)
    for face in faces:
        mesh.Faces.AddFace(face)
    
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    
    doc.Objects.AddMesh(mesh)
    
    print("Generated Morphing Mesh Landscape!")

# =====================================================================
# GENERATION FUNCTION 15: PARAMETRIC SPACE FRAME
# =====================================================================
def generate_parametric_space_frame():
    """Generate a complex space frame structure with parametric joints"""
    clear_document()
    
    def create_space_frame_node(position, connections):
        # Create node sphere
        node_sphere = rg.Sphere(position, 0.3)
        node_brep = node_sphere.ToBrep()
        doc.Objects.AddBrep(node_brep)
        
        # Create connecting members as lines
        for connection in connections:
            line = rg.Line(position, connection)
            doc.Objects.AddCurve(line.ToNurbsCurve())
    
    # Define space frame grid
    grid_size = 6
    spacing = 4
    nodes = {}
    
    # Create 3D grid of nodes
    for x in range(grid_size):
        for y in range(grid_size):
            for z in range(grid_size):
                # Add some randomness to create interesting geometry
                offset_x = random.uniform(-0.5, 0.5)
                offset_y = random.uniform(-0.5, 0.5)
                offset_z = random.uniform(-0.2, 0.2)
                
                position = rg.Point3d(
                    x * spacing + offset_x,
                    y * spacing + offset_y,
                    z * spacing + offset_z
                )
                nodes[(x, y, z)] = position
    
    # Create connections and build structure
    for (x, y, z), position in nodes.items():
        connections = []
        
        # Connect to adjacent nodes
        directions = [
            (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
            (1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0),
            (1, 0, 1), (1, 0, -1), (-1, 0, 1), (-1, 0, -1),
            (0, 1, 1), (0, 1, -1), (0, -1, 1), (0, -1, -1)
        ]
        
        for dx, dy, dz in directions:
            neighbor_key = (x + dx, y + dy, z + dz)
            if neighbor_key in nodes:
                connections.append(nodes[neighbor_key])
        
        # Only create connections for some nodes to avoid overcrowding
        if len(connections) > 3 and random.random() > 0.3:
            create_space_frame_node(position, connections[:6])  # Limit connections
    
    print("Generated Parametric Space Frame!")

# =====================================================================
# MAIN EXECUTION
# =====================================================================
def main():
    """Execute all generation functions automatically"""
    print("Rhino.Inside.Cpython Generation Functions Collection")
    print("=" * 60)
    print("Generating all 15 functions automatically...")
    print("Each will be saved as a separate Rhino file in Desktop/RhinoAuto/")
    print()
    
    functions = [
        ("01_Fibonacci_Spiral_Tower", generate_fibonacci_spiral_tower),
        ("02_Voronoi_Cityscape", generate_voronoi_cityscape),
        ("03_Parametric_Wave_Surface", generate_parametric_wave_surface),
        ("04_Fractal_Tree", generate_fractal_tree),
        ("05_Geodesic_Dome_Variations", generate_geodesic_dome_variations),
        ("06_3D_Lissajous_Curves", generate_lissajous_curves_3d),
        ("07_Cellular_Automata_Structures", generate_cellular_automata_structures),
        ("08_Twisted_Spire_Collection", generate_twisted_spire_collection),
        ("09_Parametric_Coral_Reef", generate_parametric_coral_reef),
        ("10_Hyperbolic_Paraboloid_Pavilion", generate_hyperbolic_paraboloid_pavilion),
        ("11_Particle_System_Constellation", generate_particle_system_constellation),
        ("12_Tensegrity_Structure_Network", generate_tensegrity_structure_network),
        ("13_Algorithmic_Flower_Garden", generate_algorithmic_flower_garden),
        ("14_Morphing_Mesh_Landscape", generate_morphing_mesh_landscape),
        ("15_Parametric_Space_Frame", generate_parametric_space_frame)
    ]
    
    generated_files = []
    
    for i, (filename, func) in enumerate(functions, 1):
        try:
            print(f"{i:2}/15 Generating {filename.replace('_', ' ')}...")
            func()
            file_path = save_and_open_file(filename)
            if file_path:
                generated_files.append(file_path)
                print(f"     ✓ Saved: {filename}.3dm")
            else:
                print(f"     ✗ Failed to save: {filename}.3dm")
        except Exception as e:
            print(f"     ✗ Error generating {filename}: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print(f"Generation completed! {len(generated_files)} files created.")
    print("\nOpening all Rhino files...")
    
    # Open all generated files
    for file_path in generated_files:
        try:
            os.startfile(file_path)
            print(f"Opened: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error opening {os.path.basename(file_path)}: {str(e)}")
    
    print(f"\nAll files saved in: {os.path.join(os.path.expanduser('~'), 'Desktop', 'RhinoAuto')}")

if __name__ == "__main__":
    main()
