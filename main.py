from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo, translate_zenit
from math import radians
import matplotlib.pyplot as plt
from flux_density_utils import *
from paths_in_this_machine import *
from paths_in_this_machine import root_simulations_directory

root_dir = root_simulations_directory

for sim_dir_name in os.listdir(root_dir):

    sim_dir = os.path.join(root_dir, sim_dir_name)

    if sim_dir_name == 'past' or 'data' not in os.listdir(sim_dir):
        print(f'Unknown directory name: {sim_dir}')
        continue

    sim_info = AgnSimulationInfo.build_agn_simulation_info(
        sim_root_dir=sim_dir)

    print(sim_info)

    builder = SpectraBuilder(sim_info=sim_info,
                             photon_registration_policy=NHPhotonRegistrationPolicy(simulation_info=sim_info))

    spectra = builder.build(translate_zenit(AngularInterval(
        beg=radians(60), length=radians(15))))

    print_spectra(output_dir=os.path.join(sim_info.sim_root_dir, 'THETA_6075_nh_grid'),
                  spectra=spectra)

    spectra = builder.build(translate_zenit(AngularInterval(
        beg=radians(75), length=radians(15))))

    print_spectra(output_dir=os.path.join(sim_info.sim_root_dir, 'THETA_7590_nh_grid'),
                  spectra=spectra)
