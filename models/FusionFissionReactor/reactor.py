# FILE: main_simulation.py

import openmc
import openmc.deplete
import sys
import os

from blanket import build_u238_sphere


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

# Import the functions from your other files
from neutronsource import create_cylindrical_source

# -------------------- Simulation Parameters --------------------
# Source parameters
cyl_H = 5.0
cyl_R = 1.0
E_min, E_max = 2.3e6, 2.5e6

# Geometry parameters
u238_sphere_radius = 50.0

# --- Transport Settings ---
# Particles for EACH depletion step
particles_per_batch = 10_000
num_batches = 10 

# --- Depletion Parameters ---
# The source strength you used in results.py
SOURCE_STRENGTH_PER_SEC = 1.0e15  # neutrons / sec

# Time step: 10 hours
# openmc.deplete uses seconds
time_hours = 10.0
time_seconds = time_hours * 3600.0 
timesteps_in_seconds = [time_seconds] # A list of one step: [36000.0]

# Path to the chain file you downloaded
CHAIN_FILE = "models/FusionFissionReactor/chain_endfb80_pwr.xml"# ---------------------------------------------------------------

print("Building model...")
# 1. Create the Neutron Source
my_source = create_cylindrical_source(
    height=cyl_H,
    radius=cyl_R,
    e_min=E_min,
    e_max=E_max
)

# 2. Create the Geometry and Materials
# (This will use your modified model_definition.py)
(my_geometry, my_materials) = build_u238_sphere(
    sphere_radius=u238_sphere_radius,
    world_padding=50.0
)

# 3. Define Settings for the transport "snapshot"
settings = openmc.Settings()
settings.run_mode  = 'fixed source'
settings.particles = particles_per_batch
settings.batches   = num_batches
settings.source    = my_source
settings.max_lost_particles = 1000000

# 4. Create the main OpenMC model
# This bundles everything together for the depletion operator
model = openmc.Model(geometry=my_geometry, materials=my_materials, settings=settings)

# 5. Set up the Depletion Operator
print("Setting up depletion operator...")
operator = openmc.deplete.CoupledOperator(
    model=model,
    chain_file=CHAIN_FILE,
    reduce_chain=True,       # Simplifies the chain to only what's needed
    reduce_chain_level=5,
    normalization_mode="source-rate"
)

# 6. Set up the Integrator (the "how to run")
# We use PredictorIntegrator, a good standard choice
# We give it the operator, the time steps, and the source rate
integrator = openmc.deplete.PredictorIntegrator(
    operator=operator,
    timesteps=timesteps_in_seconds, 
    source_rates=[SOURCE_STRENGTH_PER_SEC], # neutrons/sec
    timestep_units='s'
)

# 7. Run the depletion simulation!
# This replaces the simple "openmc.run()"
print(f"Running depletion for {time_hours} hours...")
integrator.integrate()

print("Depletion simulation complete. Results are in 'depletion_results.h5'")