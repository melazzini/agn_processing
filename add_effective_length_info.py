from os import listdir, path
from agn_utils import AgnSimulationInfo
import subprocess
from paths_in_this_machine import root_simulations_directory, update_effective_length_6_columns
from functools import reduce

root_dir = root_simulations_directory
update_effective_length_6_columns = update_effective_length_6_columns

print('=====================================')
for sim_dir in listdir(root_dir):
    if sim_dir == 'past' or '-1' in sim_dir:
        print(f'past or smooth torus: {sim_dir}')
        continue
    print(f'processing sim dir: {sim_dir}')
    sim_info = AgnSimulationInfo.build_agn_simulation_info(
        sim_root_dir=path.join(root_dir, sim_dir))
    print(sim_info)

    photon_files = reduce(lambda file_i, file_j: file_i +
                          ' ' + file_j, sim_info.simulation_files)

    rv = subprocess.call([update_effective_length_6_columns,
                          str(sim_info.r_clouds/100),
                          str(sim_info.n_clouds),
                          sim_info.clouds_file_path,
                          *sim_info.simulation_files])

    if rv != 0:
        print(f'There was a problem with {sim_dir}')
        exit(-1)

    print('=====================================')
