from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo, translate_zenit
from math import radians
import matplotlib.pyplot as plt
from flux_density_utils import *
from paths_in_this_machine import *
# empty_spectrum = PoissonSpectrumCountFactory.build_log_empty_spectrum_count(
#     100, 300_000, 2000)

# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)
# count_photon_into_log_spectrum(empty_spectrum, 6404)

# for i, item in enumerate(empty_spectrum):
#     print(f'{i}:    {item}')


# agn_info = AgnSimulationInfo.build_agn_simulation_info(
#     '/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/224_3_03_05xfe_c301wp_250M_lp01')

# print(agn_info)

# sim_info = AgnSimulationInfo.build_agn_simulation_info(
#     '/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe')

# builder = SpectraBuilder(sim_info=sim_info,
#                          photon_registration_policy=NHPhotonRegistrationPolicy(simulation_info=sim_info))


# spectra = builder.build(translate_zenit(AngularInterval(
#     beg=radians(60), length=radians(15))))

# print_spectra(output_dir='/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe/THETA_6075_nh_grid',spectra=spectra)

# data = np.loadtxt(
#     "/home/francisco/Projects/agn/agn_processing/23_5_03_1xfe/directions/effectiveLengths")
# counts, bins = np.histogram(data, bins=50)

# plt.plot(bins[:-1], counts/sum(counts))
# print(f'the sum is: {sum(counts/sum(counts))}')
# plt.show()

nh = 1e23

nh_grid = ColumnDensityGrid(
    left_nh=LEFT_NH, right_nh=RIGHT_NH, n_intervals=NH_INTERVALS)
index = nh_grid.index(nh)
spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
    f'/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe/THETA_6075_nh_grid/{index}_SCATTERING_NONE.spectrum')

source_spectrum_file_path = generate_source_spectrum_count_file(
    num_of_photons=500_000000, bins=2000)

source_spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
    source_spectrum_file_path)

angle_interval = AngularInterval(60, 15).from_deg_to_rad()


effective_lengths = get_effective_lengths(
    path_to_effective_lengths_file=PATH_TO_TEST_EFFECTIVE_LENGTHS)

sim_info = AgnSimulationInfo.build_agn_simulation_info(
    sim_root_dir=PATH_TO_TEST_ROOT_DIR)

nh_list = build_nh_list_from_effective_lengths(
    effective_lengths=effective_lengths, sim_info=sim_info)

nh_distribution = ColumnDensityDistribution(nh_grid=nh_grid, nh_list=nh_list)

flux_density = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum, norm_spectrum=source_spectrum, angle_interval=angle_interval,
                                                                  nh=nh, nh_distribution=nh_distribution)

source_flux_density = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=source_spectrum,
                                                                         norm_spectrum=source_spectrum,
                                                                         angle_interval=AngularInterval(
                                                                             60, 30).from_deg_to_rad(),
                                                                         nh=nh, nh_distribution=nh_distribution)

plt.plot(source_flux_density.x, source_flux_density.y)
plt.plot(flux_density.x, flux_density.y)

plt.xscale('log')
plt.yscale('log')
plt.show()
