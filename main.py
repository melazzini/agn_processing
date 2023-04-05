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

effective_lengths = get_effective_lengths(
    path_to_effective_lengths_file=PATH_TO_TEST_EFFECTIVE_LENGTHS)

sim_info = AgnSimulationInfo.build_agn_simulation_info(
    sim_root_dir=PATH_TO_TEST_ROOT_DIR)

nh_list = build_nh_list_from_effective_lengths(
    effective_lengths=effective_lengths, sim_info=sim_info)

nh_distribution = ColumnDensityDistribution(nh_grid=nh_grid, nh_list=nh_list)

plt.grid()

nh_values = []
nh_distribution_values = []

for nh in nh_distribution.grid.nh_list:
    distribution_value = nh_distribution.get_distribution_value_for_nh(nh=nh)
    nh_values += [nh]
    nh_distribution_values += [distribution_value]

plt.plot(nh_values, nh_distribution_values)


# plt.legend(prop={'size': 9})
plt.xscale('log')
# plt.yscale('log')
plt.subplots_adjust(
    top=0.95,
    bottom=0.08,
    left=0.10,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.xlabel(r'$N_{H,LOS}, cm^{-2}$')
plt.title(
    r'$<N_H> = 10^{23} cm^{-2}$, <N> =5, $\alpha=60^{\circ}$, $A_{Fe}=1$')
# plt.xlim(100, 300_000)
plt.show()
