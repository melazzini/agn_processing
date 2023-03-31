from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo, translate_zenit
from math import radians

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

sim_info = AgnSimulationInfo.build_agn_simulation_info(
    '/home/francisco/Projects/agn/columndensity/build/results/test')

builder = SpectraBuilder(sim_info=sim_info,
                         photon_registration_policy=NHPhotonRegistrationPolicy(simulation_info=sim_info))


spectra = builder.build(translate_zenit(AngularInterval(
    beg=radians(60), length=radians(15))))

print_spectra(output_dir='/home/francisco/Projects/agn/columndensity/build/results/test/outputdir',spectra=spectra)
