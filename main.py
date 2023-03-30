from spectrum_utils import *
from colum_density_utils import *
from agn_utils import AgnSimulationInfo
from math import radians

empty_spectrum = PoissonSpectrumCountFactory.build_log_empty_spectrum_count(
    100, 300_000, 2000)

count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)
count_photon_into_log_spectrum(empty_spectrum, 6404)

for i, item in enumerate(empty_spectrum):
    print(f'{i}:    {item}')


agn_info = AgnSimulationInfo.build_agn_simulation_info(
    '/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/224_3_03_05xfe_c301wp_250M_lp01')

print(agn_info)


builder = SpectraBuilder(
    '/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/224_3_03_05xfe_c301wp_250M_lp01')

builder.build(AngularInterval(beg=radians(60), length=radians(15)))

a = AngularInterval(60, -15)

print(44.9 in a)
