"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from spectral_data_utils import *
from colum_density_utils import get_all_effective_lengths, build_nh_list_from_effective_lengths, ColumnDensityDistribution
from dataclasses import dataclass
from spectrum_utils import SpectrumCount, PoissonSpectrumCountFactory, generate_source_spectrum_count_file, print_spectra
from flux_density_utils import FluxDensityBuilder, FULL_TORUS_ANGLE_DEG
import matplotlib.pyplot as plt

nh_aver = 2e23
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


grouped_spectra_files = get_grouped_spectra_files(spectra_dirs=spectra_dirs)


def group_spectra(grouped_spectra_files: Dict[SpectrumKind, List[str]]) -> Dict[SpectrumKind, SpectrumCount]:

    return {
        k: PoissonSpectrumCountFactory.build_spectrum_count(*grouped_spectra_files[k]) for k in grouped_spectra_files}


grouped_spectra = group_spectra(
    grouped_spectra_files=grouped_spectra_files)


source_spectrum_file_path = generate_source_spectrum_count_file(
    num_of_photons=n_photons, bins=HV_N_INTERVALS)

source_spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
    source_spectrum_file_path)


source_flux_density = FluxDensityBuilder.build_norm_flux_density(norm_spectrum=source_spectrum,
                                                                 angle_interval=FULL_TORUS_ANGLE_DEG.from_deg_to_rad())

continuum_spectra = build_continuum_spectra_map(
    grouped_spectra=grouped_spectra)


data_map = build_key_spectrum_flux_density_map(
    grouped_spectra=continuum_spectra,
    nh_distribution=nh_distribution,
    source_spectrum=source_spectrum,
    alpha_deg=alpha)


alpha_lbl = None

for k in AGN_VIEWING_DIRECTIONS_DEG:
    if AGN_VIEWING_DIRECTIONS_DEG[k] == alpha:
        alpha_lbl = k
        break

for kind in data_map:
    label = f'{get_nh_aver_label(sims_root_dir=sims_root_dir)}_{n_aver}_{IRON_ABUNDANCES[a_fe]}_{alpha_lbl}_{NH_INTERVALS}_{LEFT_NH:0.2g}_{RIGHT_NH:0.2g}_{kind}'

    spectral_data_dir = os.path.join(sims_root_dir, 'spectral_data')

    if not os.path.exists(spectral_data_dir):
        os.mkdir(spectral_data_dir)

    print_spectra(spectral_data_dir, {label+'.spectrum': data_map[kind][0]})

    print_spectra(spectral_data_dir, {label+'.fluxdensity': data_map[kind][1]})


fekalpha_spectra = build_fekalpha_spectra_map(
    grouped_spectra=grouped_spectra)


data_map = build_key_spectrum_flux_density_map(
    grouped_spectra=fekalpha_spectra,
    nh_distribution=nh_distribution,
    source_spectrum=source_spectrum,
    alpha_deg=alpha)


for kind in data_map:
    label = f'{get_nh_aver_label(sims_root_dir=sims_root_dir)}_{n_aver}_{IRON_ABUNDANCES[a_fe]}_{alpha_lbl}_{NH_INTERVALS}_{LEFT_NH:0.2g}_{RIGHT_NH:0.2g}_{kind}'

    spectral_data_dir = os.path.join(sims_root_dir, 'spectral_data')

    if not os.path.exists(spectral_data_dir):
        os.mkdir(spectral_data_dir)

    print_spectra(spectral_data_dir, {label+'.spectrum': data_map[kind][0]})

    print_spectra(spectral_data_dir, {label+'.fluxdensity': data_map[kind][1]})

