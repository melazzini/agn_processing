"""
This script generates the spectra from a given simulations root directory.
This script considers two angles 60 and 75 degrees.

The simulations root directory should be as clean as possible, containing
only valid simulations, and not other directories.

The resulting spectra will be stored in 
    
    /sim-root-dir/THETA_{angleInterval}_nh_grid_{nh_intervals}_{nh_left}_{nh_right}/
"""


from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo, translate_zenit, AGN_VIEWING_DIRECTIONS_DEG
from math import radians
import matplotlib.pyplot as plt
from flux_density_utils import *
from paths_in_this_machine import *
from paths_in_this_machine import root_simulations_directory

root_dir = root_simulations_directory

print("============================================")
for sim_dir_name in os.listdir(root_dir):

    sim_dir = os.path.join(root_dir, sim_dir_name)

    if sim_dir_name == 'past' or os.path.isfile(sim_dir) or 'data' not in os.listdir(sim_dir):
        print(f'Unknown directory name: {sim_dir}')
        continue

    sim_info = AgnSimulationInfo.build_agn_simulation_info(
        sim_root_dir=sim_dir)

    print(sim_info)

    reg_policy = NHPhotonRegistrationPolicy(simulation_info=sim_info)

    builder = SpectraBuilder(sim_info=sim_info,
                             photon_registration_policy=reg_policy)

    for alpha_label in AGN_VIEWING_DIRECTIONS_DEG:

        alpha = AGN_VIEWING_DIRECTIONS_DEG[alpha_label]

        spectra = builder.build(translate_zenit(alpha.from_deg_to_rad()))

        print_spectra(output_dir=os.path.join(sim_info.sim_root_dir,
                                              f'THETA_{alpha_label}_nh_grid_{reg_policy.grid.n_intervals}_{reg_policy.grid.left:0.2g}_{reg_policy.grid.right:0.2g}'),
                      spectra=spectra)

    print("============================================")
