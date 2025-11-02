import openmc, math

# -------------------- Variables --------------------
# OLD: r_cm = 45.72                 # sphere radius (1.5 ft = 45.72 cm)
# --- NEW Cylinder Dimensions ---
cyl_H = 5.0                  # cm, cylinder height
cyl_R = 1.0                  # cm, cylinder radius (from 2cm diameter)
# --- End New ---

E_min, E_max = 2.3e6, 2.5e6  # energy range (eV)
particles = 10_000           # particles per batch
# Batches = Pulses
batches   = 5                # number of batches (keep small for quick test)
R_world   = 200.0            # cm, world/vacuum radius (still fine)
# ---------------------------------------------------

# Geometry: a single void cell inside a vacuum boundary
# This part is unchanged, as the world is still a void.
boundary = openmc.Sphere(r=R_world, boundary_type='vacuum')
cell = openmc.Cell(region=-boundary)     # <-- interior (must be '-')
geom = openmc.Geometry([cell])

# Source: uniform in volume (r ~ r^1 for cylinder), isotropic directions, uniform 2.3–2.5 MeV
# --- NEW Source Definition ---
# For uniform-in-volume in a cylinder, p(r) ~ r^1
r_dist  = openmc.stats.PowerLaw(0.0, cyl_R, 1.0)
phi_dist= openmc.stats.Uniform(0.0, 2.0*math.pi)
# Uniform distribution along the cylinder's height
z_dist  = openmc.stats.Uniform(-cyl_H / 2.0, cyl_H / 2.0)

# Use CylindricalIndependent instead of SphericalIndependent
space   = openmc.stats.CylindricalIndependent(r_dist, phi_dist, z_dist, origin=(0.0, 0.0, 0.0))
# --- End New ---

angle   = openmc.stats.Isotropic()                             # flight directions
energy  = openmc.stats.Uniform(E_min, E_max)                   # Random energies between E_min and E_max

src = openmc.Source(space=space, angle=angle, energy=energy)

# Settings: fixed-source
settings = openmc.Settings()
settings.run_mode  = 'fixed source'
settings.particles = particles
settings.batches   = batches
settings.source    = src
settings.max_lost_particles = 1000000

# ---------- 3D flux mesh tally (Rescaled for new geometry) ----------
# OLD: R_vis = r_cm + 50.0  # visualize out to 50 cm past the source sphere
# --- NEW MESH BOUNDS ---
# Define a visualization box that's appropriate for the small cylinder
# Let's visualize a 10x10x10 cm box centered at the origin
vis_bound = 10.0 # cm

mesh = openmc.RegularMesh()
mesh.dimension   = (60, 60, 60)  # resolution (same, but in a smaller box)
mesh.lower_left  = (-vis_bound, -vis_bound, -vis_bound)
mesh.upper_right = ( vis_bound,  vis_bound,  vis_bound)
# --- End New ---

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name="flux_3d")
flux_tally.filters = [mesh_filter]
flux_tally.scores  = ["flux"]

tallies = openmc.Tallies([flux_tally])
tallies.export_to_xml()

# Export & run (single-threaded to avoid segfault noise while testing)
geom.export_to_xml()
settings.export_to_xml()
openmc.run(threads=1)