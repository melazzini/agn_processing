from os import listdir, path, mkdir, path
from agn_utils import AgnSimulationInfo, AGN_EFFECTIVE_LENGTHS_DIR_LABEL, AGN_VIEWING_DIRECTIONS_DEG, get_effective_lengths_directions_filename
from photon_register_policy import PhotonRawInfo
from paths_in_this_machine import root_simulations_directory, create_nh_distribution
from functools import reduce
from numpy import pi

TOTAL_DIRECTIONS = 1_000_000
  
root_dir = root_simulations_directory
  
# for root_dir in ["/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_223", "/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_23", "/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_523"]:
for root_dir in ["/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_223"]:
    print('=====================================')
    for sim_dir in listdir(root_dir):
        sim_root_dir = path.join(root_dir, sim_dir)
        if sim_dir == 'past' or path.isfile(sim_root_dir) or 'data' not in listdir(sim_root_dir):
            print(f'Unknown path:: {sim_root_dir}')
            continue
        print(f'processing sim dir: {sim_dir}')
        sim_info = AgnSimulationInfo.build_agn_simulation_info(
            sim_root_dir=sim_root_dir)

        print(sim_info)
        print('====================================')

        directions_dir = path.join(
            sim_root_dir, AGN_EFFECTIVE_LENGTHS_DIR_LABEL)

        if not path.exists(directions_dir):
            mkdir(directions_dir)

        for alpha in AGN_VIEWING_DIRECTIONS_DEG:
            outputfile = path.join(
                directions_dir, get_effective_lengths_directions_filename(alpha))

            alpha_rad = AGN_VIEWING_DIRECTIONS_DEG[alpha].from_deg_to_rad()

            min_phi = pi/2 - alpha_rad.end
            max_phi = pi/2 - alpha_rad.beg

            with open(outputfile, 'w') as directions_file:
                for sim_file_path in sim_info.simulation_files:
                    with open(sim_file_path) as sim_file:
                        counter = 0
                        for line in sim_file:
                            photon_info = PhotonRawInfo.build_photon_raw_info(
                                raw_info=line)

                            if min_phi <= photon_info.phi <= max_phi:
                                directions_file.write(
                                    f'{photon_info.effective_length}\n')

                            counter += 1
                            if counter % 10000 == 0:
                                print(
                                    f'number of photons from file{sim_file_path}: {counter}')
        print('=====================================')
