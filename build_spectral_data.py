"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from spectral_data_utils import *
from colum_density_utils import get_all_effective_lengths, build_nh_list_from_effective_lengths, ColumnDensityDistribution
from dataclasses import dataclass

nh_aver = 5e23
n_aver = 2
a_fe = 1
alpha = AngularInterval(60, 15)

sims_root_dir = simulations_root_dir(nh_aver=nh_aver)

simulations = get_simulations_in_sims_root_dir(sims_root_dir=sims_root_dir,
                                               n_aver=n_aver, a_fe=a_fe)

n_photons = get_total_n_photons(simulations=simulations)


all_effective_lengths = get_all_effective_lengths(
    effective_lengths_filepaths=get_direction_filepaths(simulations=simulations, alpha=alpha))

nh_list_all = build_nh_list_from_effective_lengths(
    effective_lengths=all_effective_lengths, sim_info=simulations[0])

nh_grid = ColumnDensityGrid(
    left_nh=LEFT_NH, right_nh=RIGHT_NH, n_intervals=NH_INTERVALS)
nh_distribution = ColumnDensityDistribution(
    nh_grid=nh_grid, nh_list=nh_list_all)

spectra_dirs = get_spectra_directories(
    simulations=simulations, alpha=alpha, grid=nh_grid)


@dataclass
class SpectrumKind:
    grid_id: int
    type_label: str
    line_label: str



def get_grouped_spectra(spectra_dirs:List[str],)
