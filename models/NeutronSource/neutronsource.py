import openmc, math

# -------------------- Variables --------------------
r_cm = 45.72                 # sphere radius (1.5 ft = 45.72 cm)
E_min, E_max = 2.3e6, 2.5e6  # energy range (eV)
particles = 10_000           # particles per batch
# Batches = Pulses
batches   = 5                # number of batches (keep small for quick test)
R_world   = 200.0            # cm, world/vacuum radius (> r_cm)
# ---------------------------------------------------

# Geometry: a single void cell inside a vacuum boundary
# Vacuum = neutrons can leave the Sphere
boundary = openmc.Sphere(r=R_world, boundary_type='vacuum')
cell = openmc.Cell(region=-boundary)     # <-- interior (must be '-')
geom = openmc.Geometry([cell])

# Source: uniform in volume (r ~ r^2), isotropic directions, uniform 2.3–2.5 MeV
# Power Law: Picks random distances in a way that fills up the whole volume equally, not just the middle. So we use r_cm^2
r_dist  = openmc.stats.PowerLaw(0.0, r_cm, 2.0)                # uniform-in-volume
mu_dist = openmc.stats.Uniform(-1.0, 1.0)                      # μ = cosθ
phi_dist= openmc.stats.Uniform(0.0, 2.0*math.pi)  

# mu = up/down direction, ϕ = left/right direction
space   = openmc.stats.SphericalIndependent(r_dist, mu_dist, phi_dist, origin=(0.0, 0.0, 0.0))

angle   = openmc.stats.Isotropic()                             # flight directions
energy  = openmc.stats.Uniform(E_min, E_max)                   # Random energies between E_min and E_max

src = openmc.Source(space=space, angle=angle, energy=energy)

# Settings: fixed-source
settings = openmc.Settings()
# fixed source means this is just releasing neutrons, aka no chain reactions
# Change to 'eigenvalue' when simulating the reactor where neutrons will multiply and cause reactions
settings.run_mode  = 'fixed source'

settings.particles = particles
settings.batches   = batches
settings.source    = src

# Temporarily - Because this is a vacuum, the neutrons conitinue going out infinitely, so this is added to tell OpenMC to stop tracking it
settings.max_lost_particles = 1000000

# ---------- 3D flux mesh tally (source sphere + 50 cm) ----------
R_vis = r_cm + 50.0  # visualize out to 50 cm past the source sphere

mesh = openmc.RegularMesh()
mesh.dimension   = (60, 60, 60)  # resolution (bump up later if you want finer detail)
mesh.lower_left  = (-R_vis, -R_vis, -R_vis)
mesh.upper_right = ( R_vis,  R_vis,  R_vis)

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


# Notes on OpenMC
# ------------------------------------------------------------------------------
# max_lost_particles vs neutron cutoff explanation
#
# OpenMC tracks every neutron ("particle") it creates. Each neutron’s life ends
# one of three ways:
#   1. Escapes the geometry (hits a vacuum boundary)
#   2. Gets absorbed by some material (none here, since this is vacuum)
#   3. Dies by cutoff – OpenMC intentionally stops tracking it because it
#      lost too much energy, bounced too long, or otherwise reached its limits.
#      -> This is NORMAL and expected.
#
# "Lost particles" are different – they mean OpenMC literally lost track of a
# neutron’s position. This happens when:
#   - The neutron spawns outside any defined cell
#   - Geometry has holes or overlaps
#   - Numerical errors occur in tracking
#      -> This is NOT normal (geometry/source problem).
#
# max_lost_particles sets how many of these “lost” neutrons OpenMC tolerates
# before stopping the run. It does NOT affect normal cutoffs.
#
# Example:
#   settings.max_lost_particles = 1_000_000
#   # allows up to 1e6 lost particles before OpenMC aborts
# ------------------------------------------------------------------------------
