#create a spent fuel waste disposal model
import openmc
import math

#Spent fuel material
m99 = openmc.Material(99,'UO2 Spent Fuel')
m99.set_density('atom/b-cm',7.133315757E-02)
m99.add_nuclide('O16',6.7187968E-01)
m99.add_nuclide('U238',3.0769658E-01)
m99.add_nuclide('U235',3.4979859E-03)
m99.add_nuclide('Pu239',2.5718196E-03)
m99.add_nuclide('U236',2.1091663E-03)
m99.add_nuclide('Cs137',1.0510726E-03)
m99.add_nuclide('Pu240',1.0215150E-03)
m99.add_nuclide('Cs133',9.7963234E-04)
m99.add_nuclide('Tc99',9.3559531E-04)
m99.add_nuclide('Ru101',9.1992123E-04)
m99.add_nuclide('Zr93',8.9218967E-04)
m99.add_nuclide('Mo95',8.5245707E-04)
m99.add_nuclide('Sr90',6.7977794E-04)
m99.add_nuclide('Pu241',6.7015516E-04)
m99.add_nuclide('Nd143',6.5286858E-04)
m99.add_nuclide('Nd145',5.3344636E-04)
m99.add_nuclide('Rh103',4.8652147E-04)
m99.add_nuclide('Cs135',4.8545594E-04)
m99.add_nuclide('Np237',2.7884345E-04)
m99.add_nuclide('Pu242',2.6644975E-04)
m99.add_nuclide('Pd107',2.5941176E-04)
m99.add_nuclide('Sm150',2.2788081E-04)
m99.add_nuclide('I129',1.4371885E-04)
m99.add_nuclide('Pu238',1.3101157E-04)
m99.add_nuclide('Pm147',1.0269899E-04)
m99.add_nuclide('Eu153',9.2879588E-05)
m99.add_nuclide('Sm152',8.8634337E-05)
m99.add_nuclide('Ag109',8.5141959E-05)
m99.add_nuclide('Am243',7.8638873E-05)
m99.add_nuclide('Sm147',6.6014495E-05)
m99.add_nuclide('U234',6.4111968E-05)
m99.add_nuclide('Cm244',3.2900525E-05)
m99.add_nuclide('Am241',3.1275801E-05)
m99.add_nuclide('Ru103',1.9360418E-05)
m99.add_nuclide('Sn126',1.8018478E-05)
m99.add_nuclide('Nb95',1.4824839E-05)
m99.add_nuclide('Cl36',1.4019981E-05)
m99.add_nuclide('Ca41',1.4019976E-05)
m99.add_nuclide('Ni59',1.4019973E-05)
m99.add_nuclide('Sm151',1.3614245E-05)
m99.add_nuclide('Cm242',7.3636478E-06)
m99.add_nuclide('Se79',7.0915868E-06)
m99.add_nuclide('Eu155',4.7729475E-06)
m99.add_nuclide('Pr143',2.0561139E-06)
m99.add_nuclide('Cm245',1.9560548E-06)
m99.add_nuclide('Sm149',1.9355989E-06)
m99.add_nuclide('Nd147',5.1292485E-07)
m99.add_nuclide('Cm243',3.0834446E-07)
m99.add_nuclide('Cm246',1.9481932E-07)
m99.add_nuclide('U237',1.7067631E-07)
m99.add_nuclide('Xe133',9.3481328E-08)
m99.add_nuclide('Gd155',7.6579955E-08)
m99.add_nuclide('I133',7.5534463E-08)
m99.add_nuclide('Eu152',4.5260253E-08)
m99.add_nuclide('Pu244',9.4590026E-09)
m99.add_nuclide('Np239',3.2856837E-09)
m99.add_nuclide('U233',1.2208878E-09)
m99.add_nuclide('Mo99',1.1472054E-09)


materiales = openmc.Materials([m99])


# -- Geometry: cylindrical shell (wall) made of m99 around the source --
# Notes / assumptions:
# - OpenMC uses units of centimeters for geometry. The user requested a wall
#   thickness of 1 m -> 100 cm. An inner radius must be chosen for the hollow
#   cylinder; we set a small default inner radius of 0.1 m (10 cm). You can
#   change `inner_radius_m` below to match your actual source size.
# - Cylinder height (along z) is set to 10 m (1000 cm) by default; change as
#   needed.

inner_radius_m = 0.10  # meters (assumption; adjust if needed)
thickness_m = 1.0      # meters (as requested)
height_m = 10.0        # meters (choose a finite height for the device)

# convert to centimeters for OpenMC
inner_radius = inner_radius_m * 100.0
outer_radius = (inner_radius_m + thickness_m) * 100.0
half_height = (height_m * 100.0) / 2.0

# Surfaces
cyl_inner = openmc.ZCylinder(r=inner_radius, name='cyl_inner')
cyl_outer = openmc.ZCylinder(r=outer_radius, name='cyl_outer')
z_min = openmc.ZPlane(z0=-half_height, boundary_type='vacuum', name='z_min')
z_max = openmc.ZPlane(z0= half_height, boundary_type='vacuum', name='z_max')

# Regions:
# - shell_region: between inner and outer cylinder and between z planes
# - void_region: interior void inside inner cylinder (where source will be placed)
# - outside_region: everything outside the outer cylinder
shell_region = +cyl_inner & -cyl_outer & +z_min & -z_max
void_region = -cyl_inner & +z_min & -z_max
outside_region = +cyl_outer | -z_min | +z_max

# Cells
cell_shell = openmc.Cell(name='m99_shell', fill=m99, region=shell_region)
cell_void = openmc.Cell(name='interior_void', fill=None, region=void_region)
cell_outside = openmc.Cell(name='outside', fill=None, region=outside_region)

# Universe and Geometry
root_universe = openmc.Universe(cells=[cell_shell, cell_void, cell_outside])
geom = openmc.Geometry(root_universe)

# Export materials and geometry to XML so they can be used by OpenMC runs
materiales.export_to_xml()
geom.export_to_xml()


# -- Source placeholder and Settings --
# The user mentioned they have a custom cylindrical isotropic line source defined
# in another file (2 cm in length). If you want to use that, replace the
# `point_source` below with the imported source object. Example (commented):
# from my_sources import cylindrical_line_source
# source = cylindrical_line_source()  # <-- the user's implementation
#
# For now we use a simple isotropic point source at the origin with a single
# neutron energy of 2.45 MeV (2.45e6 eV).

line_energy_eV = 2.45e6

# Create a cylindrical isotropic line source centered at the origin.
# The source is on the cylinder axis (r=0) and extends along z for 2 cm total.
line_length_cm = 2.0
half_line = line_length_cm / 2.0

# Radial distribution: point on axis (r=0). Phi uniform but irrelevant at r=0.
r_dist = openmc.stats.Delta(0.0)
phi_dist = openmc.stats.Uniform(0.0, 2.0 * math.pi)
z_dist = openmc.stats.Uniform(-half_line, half_line)

line_space = openmc.stats.CylindricalIndependent(r_dist, phi_dist, z_dist)

line_source = openmc.Source()
line_source.space = line_space
line_source.angle = openmc.stats.Isotropic()
line_source.energy = openmc.stats.Discrete([line_energy_eV], [1.0])
line_source.particle = 'neutron'

settings = openmc.Settings()
settings.batches = 50
settings.inactive = 10
settings.particles = 2000
settings.source = line_source
settings.run_mode = 'fixed source'
settings.export_to_xml()

# End of waste disposal geometry file
openmc.run()
