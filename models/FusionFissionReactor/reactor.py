# FILE: main_simulation.py

import openmc
# Import the functions from your other files
from blanket import build_u238_sphere
import sys
import os

# --- This block "makes it public" ---
# Get the path to the current file's folder (e.g., .../FusionFissionReactor)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the parent folder (e.g., .../models)
models_dir = os.path.dirname(current_file_dir)
# Get the path to the folder you want to import from (e.g., .../models/NeutronSource)
source_dir = os.path.join(models_dir, 'NeutronSource')

# Add that folder to Python's "search path"
if source_dir not in sys.path:
    sys.path.append(source_dir)
# --- End of block ---

# Now this import will work, because Python knows where to look!
from neutronsource import create_cylindrical_source

# -------------------- Simulation Parameters --------------------
# Source parameters
cyl_H = 5.0                  # cm, cylinder height
cyl_R = 1.0                  # cm, cylinder radius
E_min, E_max = 2.3e6, 2.5e6  # energy range (eV)

# Geometry parameters
u238_sphere_radius = 50.0    # cm
world_radius = u238_sphere_radius + 50.0 # Total simulation radius

# Settings parameters
particles_per_batch = 10_000
num_batches = 5
# ---------------------------------------------------------------

# 1. Create the Neutron Source
print("Creating neutron source...")
my_source = create_cylindrical_source(
    height=cyl_H,
    radius=cyl_R,
    e_min=E_min,
    e_max=E_max
)

# 2. Create the Geometry and Materials
print("Building geometry...")
(my_geometry, my_materials) = build_u238_sphere(
    sphere_radius=u238_sphere_radius,
    world_padding=50.0 # 50cm of vacuum outside the sphere
)

# 3. Define Settings
print("Configuring settings...")
settings = openmc.Settings()
settings.run_mode  = 'fixed source'
settings.particles = particles_per_batch
settings.batches   = num_batches
settings.source    = my_source  # <-- Here! You inject the source object
settings.max_lost_particles = 1000000

# 4. Define Tallies (Updated for the new geometry)
# Create a mesh tally that covers the whole geometry
mesh = openmc.RegularMesh()
mesh.dimension   = (100, 100, 100) # (x, y, z) bins
mesh.lower_left  = (-world_radius, -world_radius, -world_radius)
mesh.upper_right = ( world_radius,  world_radius,  world_radius)

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name="power_tally")
flux_tally.filters = [mesh_filter]
flux_tally.scores  = ["flux", "fission", "heating", "(n,gamma)"] # <-- ADDED SCORES HERE
tallies = openmc.Tallies([flux_tally])

# 5. Export XMLs and Run
print("Exporting XML files...")
my_materials.export_to_xml()
my_geometry.export_to_xml()
settings.export_to_xml()
tallies.export_to_xml()

print("Running OpenMC...")
openmc.run(threads=1)
print("Simulation complete.")