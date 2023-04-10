from os import listdir, path, mkdir, path
from agn_utils import AgnSimulationInfo, AGN_EFFECTIVE_LENGTHS_DIR_LABEL, AGN_VIEWING_DIRECTIONS_DEG, get_effective_lengths_directions_filename
import subprocess
from paths_in_this_machine import root_simulations_directory, create_nh_distribution
from functools import reduce

TOTAL_DIRECTIONS = 100_000

root_dir = root_simulations_directory

for root_dir in ["/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_223", "/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_23", "/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_523"]:
    print('=====================================')
    for sim_dir in listdir(root_dir):
        sim_root_dir = path.join(root_dir, sim_dir)
        if sim_dir == 'past' or path.isfile(sim_root_dir) or 'data' not in listdir(sim_root_dir):
            print(f'Unknown path:: {sim_root_dir}')
            continue
        print(f'processing sim dir: {sim_dir}')
        sim_info = AgnSimulationInfo.build_agn_simulation_info(
            sim_root_dir=sim_root_dir)
        
        if not sim_info.is_smooth:
            continue

        print(sim_info)

        directions_dir = path.join(
            sim_root_dir, AGN_EFFECTIVE_LENGTHS_DIR_LABEL)

        if not path.exists(directions_dir):
            mkdir(directions_dir)

        if len(listdir(directions_dir)) > 0:
            continue

        for alpha in AGN_VIEWING_DIRECTIONS_DEG:
            outputfile = path.join(
                directions_dir, get_effective_lengths_directions_filename(alpha))

            print(create_nh_distribution,
                                  str(sim_info.r_clouds/100),
                                  str(sim_info.n_clouds),
                                  sim_info.clouds_file_path,
                                  outputfile,
                                  f'{TOTAL_DIRECTIONS}',
                                  f'{AGN_VIEWING_DIRECTIONS_DEG[alpha].beg}',
                                  f'{AGN_VIEWING_DIRECTIONS_DEG[alpha].length}')

            rv = subprocess.call([create_nh_distribution,
                                  str(sim_info.r_clouds/100),
                                  str(sim_info.n_clouds),
                                  sim_info.clouds_file_path,
                                  outputfile,
                                  f'{TOTAL_DIRECTIONS}',
                                  f'{AGN_VIEWING_DIRECTIONS_DEG[alpha].beg}',
                                  f'{AGN_VIEWING_DIRECTIONS_DEG[alpha].end}'])

            if rv != 0:
                print(f'There was a problem with {sim_dir}')
                exit(-1)

        print('=====================================')
