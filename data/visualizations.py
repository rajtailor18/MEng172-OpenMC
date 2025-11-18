# FILE: plot_3d_heat.py

import openmc
import numpy as np
import plotly.graph_objects as go

print("Loading statepoint file...")
# Load the statepoint from the T=0 simulation
sp = openmc.StatePoint('openmc_simulation_n0.h5')

print("Getting tally data...")
# Get the 3D tally by its name
tally = sp.get_tally(name='3d_heating_tally')

# Get the heating data from the tally
# .mean gets the data, .flatten() makes it a 1D array
data = tally.get_slice(scores=['heating']).mean.flatten()

# Get the mesh dimensions (e.g., (80, 80, 80))
dim = tally.filters[0].mesh.dimension

# Get the x, y, z coordinates of the mesh
x, y, z = (tally.filters[0].mesh.vertices[i] for i in [0, 1, 2])

# --- IMPORTANT ---
# The data is 1D, but Plotly needs a 3D grid.
# We reshape the data array to match the mesh dimensions
# Note: 'F' order is crucial, as OpenMC data is Fortran-ordered
value_grid = data.reshape(dim, order='F')

print("Generating 3D plot...")
# Create a Plotly Volume plot
fig = go.Figure(data=go.Volume(
    x=x,
    y=y,
    z=z,
    value=value_grid,
    isomin=0.0,  # Don't show where heat is zero
    isomax=np.max(value_grid), # Set max to the hottest point
    opacity=0.2, # Low opacity to see through the "cloud"
    surface_count=20, # More surfaces = more detail
    colorscale='hot' # Use a "hot" colorscale (black-red-yellow-white)
))

# Set a dark background and make the scene fill the screen
fig.update_layout(
    scene_camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
    scene_xaxis_title="X (cm)",
    scene_yaxis_title="Y (cm)",
    scene_zaxis_title="Z (cm)",
    template="plotly_dark"
)

output_filename = "3d_heat_plot.html"
fig.write_html(output_filename, auto_open=True)

print(f"Success! Saved plot to {output_filename}")