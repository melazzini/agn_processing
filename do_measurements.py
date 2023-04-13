from measurements import *

nh_grid = ColumnDensityGrid(
    left_nh=LEFT_NH, right_nh=RIGHT_NH, n_intervals=NH_INTERVALS)
considered_nh_indexes = [nh_grid.index(nh) for nh in [1e23, 2e23, 5e23]]
considered_root_dirs = [
    "/home/francisco/Projects/agn/agn_processing/results/temporary_links"]
output_filepath = "/home/francisco/Projects/agn/agn_processing/results/errors.log"

perform_measurements(considered_nh_indexes,
                     output_filepath,
                     *considered_root_dirs)
