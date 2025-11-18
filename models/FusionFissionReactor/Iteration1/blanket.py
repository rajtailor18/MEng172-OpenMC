import openmc
import math

def build_u238_sphere(sphere_radius, world_padding=50.0):
    """
    Builds a geometry with a HOLLOW U-238 sphere (shell) at the center,
    surrounded by vacuum.

    - Inner radius = 0.5 * outer radius
    - Units: centimeters
    - Returns: (geometry, materials)
    """

    # 1) Materials
    u238 = openmc.Material(name='U-238')
    u238.add_nuclide('U238', 1.0)
    u238.set_density('g/cm3', 19.1)
    u238.depletable = True

    materials = openmc.Materials([u238])

    # 2) Geometry
    outer_radius = float(sphere_radius)
    inner_radius = 0.5 * outer_radius
    world_radius = outer_radius + float(world_padding)

    inner_surface = openmc.Sphere(r=inner_radius)
    outer_surface = openmc.Sphere(r=outer_radius)
    world_boundary = openmc.Sphere(r=world_radius, boundary_type='reflective')

    # Cells
    inner_vacuum_cell = openmc.Cell(
        name='inner_vacuum',
        region=-inner_surface
    )

    shell_cell = openmc.Cell(
        name='u238_shell',
        fill=u238,
        region=+inner_surface & -outer_surface
    )

    # 3) VOL: compute spherical shell volume and set it on the MATERIAL (for depletion)
    shell_volume = (4.0/3.0) * math.pi * (outer_radius**3 - inner_radius**3)
    u238.volume = shell_volume                      # <-- critical for depletion
    shell_cell.volume = shell_volume                # optional; nice for bookkeeping

    outer_vacuum_cell = openmc.Cell(
        name='outer_vacuum',
        region=+outer_surface & -world_boundary
    )

    root_universe = openmc.Universe(cells=[inner_vacuum_cell, shell_cell, outer_vacuum_cell])
    geometry = openmc.Geometry(root_universe)

    return geometry, materials
