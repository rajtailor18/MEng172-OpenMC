import numpy as np # needed for array indexing of the times
import h5py # needed to read finished depletion model from the reactor simulation
import openmc.deplete # to create depletion results object of type OpenMC
import math
import os
import pandas as pd

# Constants
U238_MAT_NAME = "1"  # Named 1 in blanket.py
MEV_PER_FISSION = 200.0 # On Avg - Checked for U-238
MEV_TO_JOULES = 1.60218e-13

print("Reading depletion results...")
results = openmc.deplete.Results("depletion_results.h5")
times_s = np.array(results.get_times(time_units='s'))  # 's'|'min'|'h'|'d'
assert len(times_s) >= 2, "Depletion Model does not have enough data"

# Get fission rates
# Could also use '(n,gamma)' for capture, '(n,p)' for proton emission
# Tuple (time array, corresponding reaction rate array)
_, u238_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'U238', 'fission')
_, u235_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'U235', 'fission')
_, cm244_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'Cm244', 'fission')

try:
    _, pu239_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'Pu239', 'fission')
    _, pu240_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'Pu240', 'fission')
    _, pu241_fiss_rate = results.get_reaction_rate(U238_MAT_NAME, 'Pu241', 'fission')

except KeyError:
    pu239_fiss_rate = np.zeros_like(u238_fiss_rate)

idx_start = 0
idx_end = -1

fiss_rate = u238_fiss_rate + pu239_fiss_rate + u235_fiss_rate + cm244_fiss_rate + pu240_fiss_rate + pu241_fiss_rate
#fiss_rate = u238_fiss_rate + pu239_fiss_rate 

fissions_at_start   = float(fiss_rate[idx_start])
fissions_at_10hours = float(fiss_rate[idx_end])

# Get mass
try:
    t_mass, pu239_mass = results.get_mass(U238_MAT_NAME, 'Pu239')
    total_pu239_grams = float(pu239_mass[idx_end])
except (ValueError, KeyError):
    total_pu239_grams = 0.0

power_at_start_calc = fissions_at_start * MEV_PER_FISSION * MEV_TO_JOULES
power_at_end_calc = fissions_at_10hours * MEV_PER_FISSION * MEV_TO_JOULES

openmc.config['chain_file'] = '/workspaces/MEng172-OpenMC/models/FusionFissionReactor/Iteration1/chain_endfb80_pwr.xml'

_, total_decay_heat = results.get_decay_heat(U238_MAT_NAME, units='W')

times_s = np.array(results.get_times(time_units='s'))  # 's'|'min'|'h'|'d'
assert len(times_s) >= 2, "Expected at least two depletion steps."

def getReactorUpTime(times_s, idx_start, idx_end):
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

    time_start_s = float(times_s[idx_start])
    time_end_s   = float(times_s[idx_end])
    duration_s   = time_end_s - time_start_s
    return duration_s


duration = getReactorUpTime(times_s, idx_start, idx_end)

print()
print(f"Reactor Metrics: Uptime - {duration} s")
print(f"Reactor Metrics: Total Decay Heat - {total_decay_heat[1]} W")

#removed to use a integration method instead
#avg_power_watts = (power_at_start_calc + power_at_end_calc) / 2.0
#total_energy_joules = avg_power_watts * duration
#total_energy_kwh = total_energy_joules / (3.6e6) 

#integration method for power average over time
power_array = fiss_rate * MEV_PER_FISSION * MEV_TO_JOULES
dt = np.diff(times_s, prepend=0.0)
total_energy_joules = np.sum(power_array * dt)
total_energy_kwh = total_energy_joules / (3.6e6) 

print(f"Reactor Metrics: Power (kWh) - {total_energy_kwh} kWh")
print(f"                       (or {total_energy_joules:.2f} Joules)")
t_mass, pu239_mass = results.get_mass(U238_MAT_NAME, 'Pu239')
t_mass, cm244_mass = results.get_mass(U238_MAT_NAME, 'Cm244')

initial_cm244_mass = float(cm244_mass[0])
final_cm244_mass   = float(cm244_mass[idx_end])
delta_cm244_mass   = final_cm244_mass - initial_cm244_mass

initial_pu239_grams = float(pu239_mass[0])
final_pu239_grams   = float(pu239_mass[idx_end])
delta_pu239_grams   = final_pu239_grams - initial_pu239_grams

print(f"Reactor Metrics:Net Pu-239 Created(+)/Destroyed(-) {delta_pu239_grams:.6e} g")

print(f"Reactor Metrics:Net Cm-244 Created(+)/Destroyed(-) {delta_cm244_mass:.6e} g")

print(f"Reactor Metrics: Power @ Start (kW) - {power_at_start_calc / 1000:.2f} kW")
print(f"Reactor Metrics: Power @ End (kW) - {power_at_end_calc / 1000:.2f} kW")


sp = openmc.StatePoint('openmc_simulation_n1.h5')
flux_t = sp.get_tally(name='flux_tally')
raw_tally_value = flux_t.mean.ravel()[0]  # This is your 165.6

source_rate = 1.0e15  # n/s (Must match our simulation input)

radius = 25.5
volume_cm3 = (4/3) * math.pi * (radius ** 3)
real_flux = (raw_tally_value * source_rate) / volume_cm3

print(f"--- Results ---")
print(f"Raw Tally Mean:   {raw_tally_value:.3e} [cm per source particle]")
print(f"Material Volume:  {volume_cm3:.2f} cm^3")
print(f"Source Strength:  {source_rate:.1e} n/s")
print("-" * 30)
print(f"TRUE NEUTRON FLUX: {real_flux:.3e} n/cm^2-s")


# 3. Calculate Surface Area (m^2)
# Your geometry is a sphere with radius 25.5 cm
radius_cm = 25.5
radius_m = radius_cm / 100.0
surface_area_m2 = 4 * math.pi * (radius_m ** 2)

# 4. Calculate Heat Flux (W/m^2)
heat_flux = power_at_end_calc / surface_area_m2

print("-" * 30)
print(f"Total Heat Deposition: {power_at_end_calc:.2f} W")
print(f"Surface Area:          {surface_area_m2:.4f} m^2")
print("-" * 30)
print(f"AVERAGE HEAT FLUX:     {heat_flux:.2f} W/m^2")
print("-" * 30)

print("\nGenerating time-series arrays for graphing...")

# 1. Power Array [Watts]
# REUSE: 'fiss_rate' (the array you created earlier)
# REUSE: 'MEV_PER_FISSION' and 'MEV_TO_JOULES' constants
power_array = fiss_rate * MEV_PER_FISSION * MEV_TO_JOULES

# 2. Heat Flux Array [W/m^2]
# REUSE: 'surface_area_m2'
heat_flux_array = power_array / surface_area_m2

# 3. Neutron Flux Array [n/cm^2-s]
# We must loop through files because 'real_flux' above was just for one snapshot.
neutron_flux_list = []
num_steps = len(times_s)

print(f"Extracting flux history from {num_steps} statepoint files...")

for i in range(num_steps):
    filename = f"openmc_simulation_n{i}.h5"
    
    if os.path.exists(filename):
        try:
            with openmc.StatePoint(filename) as sp:
                # REUSE: 'flux_tally' name logic, but load new object per file
                tally = sp.get_tally(name='flux_tally')
                raw_val = tally.mean.ravel()[0]
                
                # REUSE: 'source_rate' and 'volume_cm3' from your script
                phys_flux = (raw_val * source_rate) / volume_cm3
                neutron_flux_list.append(phys_flux)
        except Exception as e:
            # Fallback if file is corrupted or tally missing
            neutron_flux_list.append(0.0)
    else:
        # Fallback if file missing
        neutron_flux_list.append(0.0)

neutron_flux_array = np.array(neutron_flux_list)

# ================= OUTPUTS FOR TEAMMATE =================
# Copy-paste these arrays to send to your teammate

print("\n" + "="*50)
print("   DATA ARRAYS FOR GRAPHING")
print("="*50)

# Using repr() to ensure full precision for copy-pasting
print(f"\n# 1. Time Steps [seconds]:")
print(repr(times_s))

print(f"\n# 2. Fission Rate [reactions/sec]:")
print(repr(fiss_rate))

print(f"\n# 3. Power [Watts]:")
print(repr(power_array))

print(f"\n# 4. Heat Flux [W/m^2]:")
print(repr(heat_flux_array))

print(f"\n# 5. Neutron Flux [n/cm^2-s]:")
print(repr(neutron_flux_array))
print("="*50)

# Constants
JOULES_PER_MWd = 8.64e10  # 1 MWd = 8.64e10 J

# 1. Get total heavy metal mass (U + Pu etc.) in kg
hm_isos = ['U238', 'U235', 'Pu239', 'Pu240', 'Pu241']
M_HM = 0.0
for iso in hm_isos:
    try:
        _, mass_arr = results.get_mass(U238_MAT_NAME, iso, mass_units='kg')
        M_HM += mass_arr[0]  # initial mass (kg)
    except (KeyError, ValueError):
        pass  # isotope not found

if M_HM == 0:
    raise RuntimeError("No heavy metal isotopes found for burnup calculation")

# 2. Integrate energy over time
#    Power array = fiss_rate * 200 MeV * 1.602e-13 J
dt = np.diff(times_s, prepend=0.0)
energy_J = np.cumsum(power_array * dt)  # J at each step

# 3. Convert to MWd/kg
burnup_MWd_per_kg = energy_J / (M_HM * JOULES_PER_MWd)

# 4. Print and export
print("\n--- BURNUP RESULTS ---")
for i, bu in enumerate(burnup_MWd_per_kg):
    print(f"Step {i:02d}: {bu:.6f} MWd/kg")

print(f"\nFinal Burnup: {burnup_MWd_per_kg[-1]:.6f} MWd/kg")

# 5. K_eff Array
#sp = openmc.StatePoint('openmc_simulation_n1.h5')
#keff = sp.k_combined  # combined estimate of k-effective
#print(f"K-effective: {keff:.6f}")

# Optional: include in your export arrays
print(f"\n# 6. Burnup [MWd/kg]:")
print(repr(burnup_MWd_per_kg))
