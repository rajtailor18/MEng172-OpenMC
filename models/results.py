import openmc

# Define your source strength (neutrons per second)
SOURCE_STRENGTH = 1.0e15  # n/s

# Define the conversion factor from MeV to Watts
# 1 MeV/s = 1.60218e-13 Joules/s (Watts)
MEV_PER_SECOND_TO_WATTS = 1.60218e-13

# --- Post-processing starts here ---
# 1. Load the statepoint file (assuming it's named 'statepoint.10.h5' for 10 batches)
sp = openmc.StatePoint('statepoint.5.h5')

# 2. Get the tally you named "power_tally"
tally = sp.get_tally(name='power_tally')

total_pu_per_particle = tally.get_slice(scores=['(n,gamma)']).mean
print(f"Total PU (from tally): {total_pu_per_particle:.4e} fissions / source particle")

# Get the fission data.
total_fissions_per_particle = tally.get_slice(scores=['fission']).mean.sum()

print(f"Total Fissions (from tally): {total_fissions_per_particle:.4e} fissions / source particle")

# 3. Get the heating data. 
# We'll sum over the whole mesh to get one total number.
# The data is in eV, so we convert to MeV.
total_heating_per_particle = tally.get_slice(scores=['heating']).mean.sum() * 1e-6 # (MeV / source particle)

# 4. Do the conversion to Power
total_power_MeV_per_second = total_heating_per_particle * SOURCE_STRENGTH
total_power_Watts = total_power_MeV_per_second * MEV_PER_SECOND_TO_WATTS

print(f"--- Power Calculation ---")
print(f"Total Heating (from tally): {total_heating_per_particle:.4e} MeV / source particle")
print(f"Source Strength (defined):  {SOURCE_STRENGTH:.4e} neutrons / sec")
print(f"Total Power (calculated): {total_power_Watts:.4e} Watts")