import glob
import numpy as np
import openmc
import plotly.graph_objects as go
from plotly.offline import plot

# --- config: must match tally ---
dims = (60, 60, 60)
r_cm  = 45.72
R_vis = r_cm + 50.0

# --- statepoint ---
candidates = sorted(glob.glob("statepoint.*.h5") + glob.glob("../statepoint.*.h5"))
if not candidates:
    raise FileNotFoundError("No statepoint.*.h5 found—run neutronsource.py first.")
sp = openmc.StatePoint(candidates[-1])

# --- data ---
t = sp.get_tally(name="flux_3d")
flux = t.mean.reshape(dims)
mx = float(flux.max())
vals = flux / (mx if mx > 0 else 1.0)

# physical coordinates for axes (so (0,0,0) is center)
nx, ny, nz = dims
xs = np.linspace(-R_vis, R_vis, nx)
ys = np.linspace(-R_vis, R_vis, ny)
zs = np.linspace(-R_vis, R_vis, nz)

# choose an isosurface level (e.g., 70% of max)
level = 0.70

fig = go.Figure(data=go.Isosurface(
    x=np.repeat(xs, ny*nz),
    y=np.tile(np.repeat(ys, nz), nx),
    z=np.tile(zs, nx*ny),
    value=vals.ravel(order="C"),
    isomin=level, isomax=vals.max(),
    surface_count=2,         # increase for multiple shells
    caps=dict(x_show=False, y_show=False, z_show=False),
    colorscale="Plasma",
))
fig.update_layout(
    title=f"Isosurface of normalized flux (≥ {int(level*100)}% of max)",
    scene=dict(
        xaxis_title="x [cm]", yaxis_title="y [cm]", zaxis_title="z [cm]",
        aspectmode="data"
    ),
)
out = "data/flux_isosurface.html"
plot(fig, filename=out, auto_open=False)
print(f"Saved: {out}")
