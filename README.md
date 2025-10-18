
# OpenMC Codespaces Starter

This repo gives you a reproducible OpenMC setup in GitHub Codespaces with Jupyter.

## One-time: Create Codespace
1. Push these files to a GitHub repo (or create the repo from this folder).
2. Click **Code → Codespaces → Create codespace on main**.
3. Wait for the container to build. When done, you'll have Jupyter ready.

## Verify OpenMC
Open a new Jupyter Notebook and run:
```python
import openmc, os
print("OpenMC:", openmc.__version__)
print("OPENMC_CROSS_SECTIONS:", os.environ.get("OPENMC_CROSS_SECTIONS"))
```

If cross sections aren't set, run in the terminal:
```bash
echo "export OPENMC_CROSS_SECTIONS=$CONDA_PREFIX/share/openmc/cross_sections.xml" >> ~/.bashrc
source ~/.bashrc
```

## Project layout
```
notebooks/   # Exploratory notebooks
models/      # Reusable model builders
runs/        # Param sweeps and batch scripts
data/        # Outputs (gitignored)
.devcontainer/  # Devcontainer setup
environment.yml
```

## Example usage
- Single-core: `openmc`
- MPI: `mpiexec -n 4 openmc`

## Notes
- The `openmc-data` package installs an HDF5 nuclear data library and `cross_sections.xml`.
- Everyone on the team will get the exact same environment when launching a Codespace.
```

