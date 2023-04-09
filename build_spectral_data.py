"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from spectral_data_utils import *
from colum_density_utils import get_all_effective_lengths, build_nh_list_from_effective_lengths, ColumnDensityDistribution
from dataclasses import dataclass
from spectrum_utils import SpectrumCount, PoissonSpectrumCountFactory, generate_source_spectrum_count_file
from flux_density_utils import FluxDensityBuilder, FULL_TORUS_ANGLE_DEG
import matplotlib.pyplot as plt

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


grouped_spectra_files = get_grouped_spectra_files(spectra_dirs=spectra_dirs)


def my_print(*files):
    for f in files:
        print(f)

    print('=====================')
    print('=====================')


def grouped_spectra(grouped_spectra_files: Dict[SpectrumKind, List[str]]) -> Dict[SpectrumKind, SpectrumCount]:

    return {
        k: PoissonSpectrumCountFactory.build_spectrum_count(*grouped_spectra_files[k]) for k in grouped_spectra_files}


grouped_spectra_map = grouped_spectra(
    grouped_spectra_files=grouped_spectra_files)


source_spectrum_file_path = generate_source_spectrum_count_file(
    num_of_photons=n_photons, bins=HV_N_INTERVALS)

source_spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
    source_spectrum_file_path)


source_flux_density = FluxDensityBuilder.build_norm_flux_density(norm_spectrum=source_spectrum,
                                                                 angle_interval=FULL_TORUS_ANGLE_DEG.from_deg_to_rad())

plt.grid()

plt.plot(source_flux_density.x, source_flux_density.y, label='source')


for nh in nh_grid.nh_list[17:18]:

    index = nh_grid.index(nh)

    flux_density = None

    for spectrum_key in grouped_spectra_map:
        if index == spectrum_key.grid_id and ("SCATTERING" == spectrum_key.type_label or "NOINTERACTION" == spectrum_key.type_label):
            spectrum = grouped_spectra_map[spectrum_key]

            flux_density_ = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum,
                                                                               norm_spectrum=source_spectrum,
                                                                               angle_interval=alpha.from_deg_to_rad(),
                                                                               nh=nh,
                                                                               nh_distribution=nh_distribution)

            if flux_density == None:
                flux_density = flux_density_
            else:
                flux_density.y += flux_density_.y

    plt.plot(flux_density.x,
             flux_density.y, label=f'{spectrum_key}, nh={nh:.2g}cm^{{-2}}')


plt.legend()
plt.xscale('log')
plt.yscale('log')
plt.show()
