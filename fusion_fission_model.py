# models/fusion_fission_model.py
import openmc

def build_model(params: dict) -> openmc.model.Model:
    """Return an OpenMC model using `params`.
    Expected keys (extend as needed):
      - fuel_enrich (float)
      - source_energy_MeV (float)
    """
    model = openmc.model.Model()

    # --- Minimal placeholder model (vacuum sphere) ---
    # Materials
    mat = openmc.Material()
    mat.set_density('g/cm3', 1.0)
    mat.add_element('H', 2.0)
    mat.add_element('O', 1.0)

    mats = openmc.Materials([mat])
    model.materials = mats

    # Geometry
    r = 50.0  # cm
    sphere = openmc.Sphere(r=r, boundary_type='vacuum')
    region = -sphere
    cell = openmc.Cell(region=region, fill=mat)
    geom = openmc.Geometry([cell])
    model.geometry = geom

    # Source (mono-energetic as placeholder)
    src = openmc.Source()
    src.space = openmc.stats.Point((0.0, 0.0, 0.0))
    src.angle = openmc.stats.Isotropic()
    src.energy = openmc.stats.Monoenergetic(params.get('source_energy_MeV', 14.1) * 1.0e6)
    model.settings = openmc.Settings()
    model.settings.batches = 10
    model.settings.inactive = 0
    model.settings.particles = 1000
    model.settings.source = src

    # Tallies (simple flux tally)
    mesh = openmc.RegularMesh()
    mesh.dimension = (10, 10, 10)
    mesh.lower_left = (-r, -r, -r)
    mesh.upper_right = ( r,  r,  r)

    mesh_filter = openmc.MeshFilter(mesh)
    tally = openmc.Tally(name='flux')
    tally.filters = [mesh_filter]
    tally.scores = ['flux']
    model.tallies = openmc.Tallies([tally])

    return model
