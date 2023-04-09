from os import listdir, path
from agn_utils import AgnSimulationInfo
import subprocess
from paths_in_this_machine import root_simulations_directory, update_effective_length_6_columns

root_dir = root_simulations_directory
update_effective_length_6_columns = update_effective_length_6_columns

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
    rv = subprocess.call([update_effective_length_6_columns,
                          str(sim_info.r_clouds/100),
                          str(sim_info.n_clouds),
                          str(sim_info.r1/100),
                          str(sim_info.r2/100),
                          str(sim_info.theta),
                          sim_info.clouds_file_path,
                          *sim_info.simulation_files])

    if rv != 0:
        print(f'There was a problem with {sim_dir}')
        exit(-1)

    print('=====================================')
