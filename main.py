from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo, translate_zenit
from math import radians
import matplotlib.pyplot as plt
from flux_density_utils import *
from paths_in_this_machine import *
from matplotlib.pyplot import figure
figure(figsize=(8, 7), dpi=120)


nh_grid = ColumnDensityGrid(
    left_nh=LEFT_NH, right_nh=RIGHT_NH, n_intervals=NH_INTERVALS)

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

source_flux_density = FluxDensityBuilder.build_norm_flux_density(norm_spectrum=source_spectrum,
                                                                 angle_interval=FULL_TORUS_ANGLE_DEG.from_deg_to_rad())

plt.grid()

plt.plot(source_flux_density.x, source_flux_density.y, label='source')

x, y_continuum = x_y(
    "/media/francisco/repo/62322/AGN_REPO/repo/N_H_23/23_-1_03_1xfe/THETA_6075/CONTINUUM_6075.txt")
x, y_fekalpha = x_y(
    "/media/francisco/repo/62322/AGN_REPO/repo/N_H_23/23_-1_03_1xfe/THETA_6075/FeKalpha.txt")

plt.plot(x, y_continuum + y_fekalpha, label = "smooth")

# exit(-1)

for nh in nh_grid.nh_list[3:4]:

    index = nh_grid.index(nh)

    spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
        f'/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe/THETA_6075_nh_grid_35_5e+22_5e+25/{index}_SCATTERING_NONE.spectrum')

    flux_density_scattering = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum, norm_spectrum=source_spectrum, angle_interval=angle_interval,
                                                                                 nh=nh, nh_distribution=nh_distribution)

    spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
        f'/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe/THETA_6075_nh_grid_35_5e+22_5e+25/{index}_NO_INTERACTIONS_NONE.spectrum')

    flux_density_no_interactions = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum, norm_spectrum=source_spectrum, angle_interval=angle_interval,
                                                                                      nh=nh, nh_distribution=nh_distribution)

    spectrum = PoissonSpectrumCountFactory.build_spectrum_count(
        f'/home/francisco/Projects/agn/columndensity3/build/results/23_5_03_1xfe/THETA_6075_nh_grid_35_5e+22_5e+25/{index}_FLUORESCENT_FeKalpha.spectrum')

    flux_density_fekalpha = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum, norm_spectrum=source_spectrum, angle_interval=angle_interval,
                                                                               nh=nh, nh_distribution=nh_distribution)

    plt.plot(flux_density_scattering.x, flux_density_scattering.y +
             flux_density_no_interactions.y+flux_density_fekalpha.y, label=r'<N> = 5, $N_{H,LOS}=$' f'{nh:0.3g}' r'$cm^{-2}$')


x, y_continuum = x_y(
    "/home/francisco/Projects/agn/agn_processing/results/build/23_5_03_1xfe/THETA_6075/CONTINUUM_6075_N=5.txt")
x, y_fekalpha = x_y(
    "/home/francisco/Projects/agn/agn_processing/results/build/23_5_03_1xfe/THETA_6075/FeKalpha5.txt")

plt.plot(x, y_continuum + y_fekalpha, label = r"<N> =N=5")


x, y_continuum = x_y(
    "/media/francisco/repo/62322/AGN_REPO/repo/N_H_23/23_3_03_1xfe/THETA_6075/CONTINUUM_6075_N=3.txt")
x, y_fekalpha = x_y(
    "/media/francisco/repo/62322/AGN_REPO/repo/N_H_23/23_3_03_1xfe/THETA_6075/FeKalpha5.txt")

plt.plot(x, y_continuum + y_fekalpha, label = r"<N> =N=3")


plt.legend(prop={'size': 9})
plt.xscale('log')
plt.yscale('log')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.12,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.xlabel(r'$eV$')
plt.ylabel(r'$E\frac{dN}{dE},\frac{eV}{cm^{2}eV}$')
plt.title(
    r'$<N_H> = 10^{23} cm^{-2}$, $\alpha=60^{\circ}$, $A_{Fe}=1$, Continuum + Fe-K$\alpha$')
plt.xlim(100, 300_000)
plt.show()
