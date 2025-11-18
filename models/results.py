# FILE: results.py

import numpy as np
import h5py
import openmc.deplete

# ---- Config ----
U238_MAT_NAME = "1"      # Or "U-238" if you re-ran with the named material
MEV_PER_FISSION = 200.0  # (Good approximation for U-238/Pu-239)
MEV_TO_JOULES = 1.60218e-13

print("Reading depletion results...")
results = openmc.deplete.Results("depletion_results.h5")
times_s = np.array(results.get_times(time_units='s'))  # 's'|'min'|'h'|'d'
assert len(times_s) >= 2, "Expected at least two depletion steps."

with h5py.File("depletion_results.h5", "r") as f:
    if "power" in f:
        power_watts = f["power"][()]
        power_watts = np.array(power_watts).reshape(-1)
    elif "source_rate" in f:
        sr = f["source_rate"][()]
        power_watts = sr[:, 0]
    else:
        raise RuntimeError("Neither 'power' nor 'source_rate' dataset found in depletion_results.h5")

if len(power_watts) != len(times_s):
    n = min(len(power_watts), len(times_s))
    power_watts = power_watts[:n]
    times_s = times_s[:n]

idx_start = 0
idx_end = -1


# Get fission rates
t_fiss, u238_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'U238', 'fission')
try:
    t_fiss, pu239_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'Pu239', 'fission')
except KeyError:
    pu239_fiss_rate = np.zeros_like(u238_fiss_rate)
fiss_rate = u238_fiss_rate + pu239_fiss_rate
fissions_at_start   = float(fiss_rate[idx_start])
fissions_at_10hours = float(fiss_rate[idx_end])

# Get mass
try:
    t_mass, pu239_mass = results.get_mass(U238_MAT_NAME, 'Pu239')
    total_pu239_grams = float(pu239_mass[idx_end])
except (ValueError, KeyError):
    total_pu239_grams = 0.0

# Calculate Instantaneous Power (Watts)
power_at_start_calc = fissions_at_start * MEV_PER_FISSION * MEV_TO_JOULES
power_at_10hours_calc = fissions_at_10hours * MEV_PER_FISSION * MEV_TO_JOULES

# --- NEW: Calculate TOTALS over the 10-hour interval ---

# Get the time duration (10 hours in seconds)
time_start_s = float(times_s[idx_start])
time_end_s   = float(times_s[idx_end])
duration_s   = time_end_s - time_start_s # Should be 36000.0

# 1. Total Energy (in Joules and kWh)
# We average the power at the start and end and multiply by time
avg_power_watts = (power_at_start_calc + power_at_10hours_calc) / 2.0
total_energy_joules = avg_power_watts * duration_s
total_energy_kwh = total_energy_joules / (3.6e6) # 3.6e6 J per kWh

# 2. Total Fissions (a raw count)
# We average the fission rate and multiply by time
avg_fission_rate = (fissions_at_start + fissions_at_10hours) / 2.0
total_fissions_count = avg_fission_rate * duration_s

# 3. Total Pu-239 (already calculated)
# total_pu239_grams is already the total created, since it starts at 0

# --- Print All Results (Now with correct power) ---
print("\n--- Instantaneous Rates (t = 0 hours) ---")
print(f"Power Rate:       {power_at_start_calc:.4e} Watts (or {power_at_start_calc / 1000:.2f} kW)")
print(f"Fission Rate:     {fissions_at_start:.4e} fissions/sec")

print("\n--- Instantaneous Rates (t = 1 year) ---")
print(f"Power Rate:       {power_at_10hours_calc:.4e} Watts (or {power_at_10hours_calc / 1000:.2f} kW)")
print(f"Fission Rate:     {fissions_at_10hours:.4e} fissions/sec")

print("\n--- TOTALS Accumulated over 1 ---")
print(f"Total Energy Produced:  {total_energy_joules:.4e} Joules")
print(f"                       (or {total_energy_kwh:.2f} kWh)")
print(f"Total Fissions (count): {total_fissions_count:.4e} fissions")
print(f"Total Pu-239 Created:   {total_pu239_grams:.6e} grams")


## Neutron flux find that and add it in
## what temp is it at?
## Burnup - thermal energy / initial mass

