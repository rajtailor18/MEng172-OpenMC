import openmc

# --- 1. Define materials ---
fuel = openmc.Material(name="UO2 fuel")
fuel.add_element('U', 1, enrichment=3.0)
fuel.add_element('O', 2)
fuel.set_density('g/cm3', 10.0)

water = openmc.Material(name="Water")
water.add_element('H', 2)
water.add_element('O', 1)
water.set_density('g/cm3', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')

materials = openmc.Materials([fuel, water])

# --- 2. Geometry ---
# --- 2. Geometry (bounded with an outer vacuum sphere) ---
fuel_region = -openmc.Sphere(r=0.39, boundary_type='transmission')  # inner sphere (finite surface)
fuel_cell   = openmc.Cell(region=fuel_region, fill=fuel)

# Outer vacuum boundary that closes the model
outer_sphere = openmc.Sphere(r=50.0, boundary_type='vacuum')
mod_region   = +openmc.Sphere(r=0.39) & -outer_sphere
mod_cell     = openmc.Cell(region=mod_region, fill=water)

geometry = openmc.Geometry([fuel_cell, mod_cell])

# --- 3. Settings ---
settings = openmc.Settings()
# Use temperature interpolation (don’t require windowed-multipole data)
settings.temperature = {'method': 'interpolation'}
settings.batches = 20
settings.inactive = 5
settings.particles = 1000
settings.source = openmc.Source(space=openmc.stats.Point((0, 0, 0)))

# --- 4. Export and run ---
materials.export_to_xml()
geometry.export_to_xml()
settings.export_to_xml()

openmc.run()

