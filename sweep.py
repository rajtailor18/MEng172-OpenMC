# runs/sweep.py
from models.fusion_fission_model import build_model
import openmc, itertools, pathlib

param_grid = {
    "fuel_enrich": [0.02, 0.035, 0.05],
    "source_energy_MeV": [2.5, 14.1],
}

out_root = pathlib.Path("../data")
out_root.mkdir(parents=True, exist_ok=True)

for combo in itertools.product(*param_grid.values()):
    params = dict(zip(param_grid.keys(), combo))
    model = build_model(params)
    model.export_to_xml()

    run_dir = out_root / f"run_e{params['fuel_enrich']}_E{params['source_energy_MeV']}"
    run_dir.mkdir(exist_ok=True, parents=True)

    # Run OpenMC in per-run directory
    openmc.run(cwd=str(run_dir))
    print("Finished:", run_dir)
