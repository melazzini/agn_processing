from measurements import *
from colum_density_utils import ColumnDensityGrid
from paths_in_this_machine import root_dirs, repo_directory
import os

nh_grid = ColumnDensityGrid(
    left_nh=LEFT_NH, right_nh=RIGHT_NH, n_intervals=NH_INTERVALS)
considered_nh_indexes = [nh_grid.index(
    nh) for nh in [1e22, 2e22, 5e22, 8e22, 1e23, 2e23, 5e23, 8e23, 1e24, 2e24, 4e24]]
considered_root_dirs = [os.path.join(
    repo_directory, root_dir) for root_dir in root_dirs]
output_filepath = os.path.join(
    repo_directory, f"{nh_grid.n_intervals}_{nh_grid.left:0.2g}_{nh_grid.right:0.2g}.measurements")

perform_measurements(considered_nh_indexes,
                     output_filepath,
                     *considered_root_dirs)
