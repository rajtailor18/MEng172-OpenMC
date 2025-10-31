# data/visualizations.py
import matplotlib
matplotlib.use("Agg")  # headless (no GUI)
import glob
import numpy as np
import openmc
import matplotlib.pyplot as plt

r_cm  = 45.72          # source radius (cm)
R_vis = r_cm + 50.0    # extend visualization 50 cm beyond the source

# --- config (set to your mesh dims) ---
dims = (60, 60, 60)  # must match mesh.dimension

# --- load newest statepoint (repo root or parent) ---
candidates = sorted(glob.glob("statepoint.*.h5") + glob.glob("../statepoint.*.h5"))
if not candidates:
    raise FileNotFoundError("No statepoint.*.h5 found — run neutronsource.py first.")
sp = openmc.StatePoint(candidates[-1])

# --- get flux and normalize ---
t = sp.get_tally(name="flux_3d")
flux = t.mean.reshape(dims)
flux /= (flux.max() if flux.max() > 0 else 1.0)

# --- Show one central slice as a heatmap png ---
mid = flux.shape[0] // 2
plt.imshow(flux[mid, :, :],
           origin="lower",
           cmap="plasma",
           extent=[-R_vis, R_vis, -R_vis, R_vis])  # <-- centers (0,0)
plt.title("Neutron Flux — Center Slice")
plt.xlabel("x [cm]")
plt.ylabel("y [cm]")
plt.colorbar(label="Normalized Flux")

# --- Save image (no GUI in Codespaces) ---
out = "data/flux_center_slice.png"
plt.savefig(out, dpi=200, bbox_inches="tight")
print(f"Saved: {out}")
