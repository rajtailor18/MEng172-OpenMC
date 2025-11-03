# FILE: model_definition.py

import openmc

def build_u238_sphere(sphere_radius, world_padding=50.0):
    """
    Builds a geometry with a HOLLOW U-238 sphere (shell) at the center,
    surrounded by a vacuum.
    
    The inner radius is half of the outer (sphere_radius).
    
    Returns a tuple: (geometry, materials)
    """
    
    # 1. Define Materials
    u238 = openmc.Material(name='U-238')
    u238.add_nuclide('U238', 1.0)
    u238.set_density('g/cm3', 19.1)
    
    materials = openmc.Materials([u238])
    
    # 2. Define Geometry
    
    # --- Updated Surfaces ---
    # The 'sphere_radius' is now the outer radius of the shell
    outer_radius = sphere_radius
    inner_radius = outer_radius / 2.0
    
    world_radius = outer_radius + world_padding
    
    # Define the three spherical surfaces
    inner_surface = openmc.Sphere(r=inner_radius)
    outer_surface = openmc.Sphere(r=outer_radius)
    world_boundary = openmc.Sphere(r=world_radius, boundary_type='vacuum')
    # --- End Update ---
    
    
    # --- Updated Cells ---
    # We now need three cells
    
    # Cell 1: Inner hollow region (inside the inner_surface)
    # The source will be born in this void region
    inner_vacuum_cell = openmc.Cell(
        name='inner_vacuum',
        region=-inner_surface  # Region is *inside* the inner surface
    )
    
    # Cell 2: The U-238 shell
    shell_cell = openmc.Cell(
        name='u238_shell',
        fill=u238,
        region=+inner_surface & -outer_surface # *Outside* inner, *Inside* outer
    )
    
    # Cell 3: Outside the shell, inside the world boundary
    outer_vacuum_cell = openmc.Cell(
        name='outer_vacuum',
        region=+outer_surface & -world_boundary # *Outside* outer, *Inside* world
    )
    # --- End Update ---

    # Universe and Geometry
    # Add all three cells to the universe
    root_universe = openmc.Universe(cells=[inner_vacuum_cell, shell_cell, outer_vacuum_cell])
    geometry = openmc.Geometry(root_universe)
    
    return (geometry, materials)