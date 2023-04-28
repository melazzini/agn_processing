from measurable_utils import get_edge_vs_h_by_nh_aver, load_data_from_file, filter_data_by_nhaver, Measurement, filter_data_by_nh
from colum_density_utils import ColumnDensityGrid, DEFAULT_NH_GRID
from agn_processing_policy import *
from agn_simulation_policy import AGN_IRON_ABUNDANCE, AGN_NH_AVERAGE
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
import numpy as np
from paths_in_this_machine import *
from matplotlib.lines import Line2D
from scipy.optimize import curve_fit
from agn_art_utils import *
from matplotlib.pyplot import figure
figure(figsize=(8, 7), dpi=120)


def fit_h_N_fit_m1(h, a, b, c):
    return a + b*np.log10(h) + c*np.log10(h)**2


used_nh_aver = '24'

data = load_data_from_file(MEASUREMENTS_FILEPATH)
data = filter_data_by_nhaver(data=data, nh_aver=used_nh_aver)

permitted_indices = [DEFAULT_NH_GRID.index(
    nh=nh) for nh in [2e23, 5e23, 1e24]]

used_indices = set()

for measurement in data:

    if measurement.key.nh_index not in permitted_indices:
        continue

    if measurement.value.edge.err/(1-measurement.value.edge.value) > 0.2:
        continue

    used_indices.add(measurement.key.nh_index)

    plt.scatter(measurement.value.h.value, 1 -
                measurement.value.edge.value, [150],
                edgecolor=ABUNDANCE_COLOR[measurement.key.a_fe],
                color=NH_COLORS[measurement.key.nh_index],
                linewidths=2,
                marker=MARKERS[measurement.key.n_aver])

    plt.errorbar(measurement.value.h.value, 1 -
                 measurement.value.edge.value, measurement.value.edge.err,
                 xerr=measurement.value.h.err,
                 color='none',
                 ecolor='black', linewidth=0.9)


used_indices = sorted(used_indices)

for index in used_indices:
    data_by_index = filter_data_by_nh(data=data, nh_index=index)

    x = []
    y = []

    for measurement in data_by_index:
        x += [measurement.value.h.value]
        y += [1-measurement.value.edge.value]

    pars, _ = curve_fit(fit_h_N_fit_m1, x, y, maxfev=1_000_000)

    x = np.linspace(min(x), max(x), num=100)
    y = fit_h_N_fit_m1(x, *pars)
    plt.plot(x, y, color=NH_COLORS[index])


plt.grid()

# lines = [
#     Line2D([0], [0], color=ABUNDANCE_COLOR[key]) for key in ABUNDANCE_COLOR
# ]

# labels = [
#     r'$A_{Fe} = $' f'{AGN_IRON_ABUNDANCE[key]}' for key in AGN_IRON_ABUNDANCE
# ]

# lines = [
#     Line2D([0], [0], markeredgecolor='black', marker=MARKERS[n_i], markersize=10, color='none') for n_i in MARKERS if n_i != 1
# ]

# labels = [
#     r'$<N> =$' f'{n_i if n_i!=NUM_OF_CLOUDS_SMOOTH else "smooth"}' for n_i in MARKERS if n_i != 1
# ]

lines = [
    Line2D([0], [0], color=NH_COLORS[index]) for index in used_indices
]

labels = [
    r'$N_H = $' f'{NH_LABELS[index]}' for index in used_indices
]


plt.legend(lines, labels)
plt.xlabel('H')
plt.ylabel(r'$1-N_{Fe}$')
plt.title(
    r'$<N_H> =$' f'{NH_LABELS[DEFAULT_NH_GRID.index(AGN_NH_AVERAGE[used_nh_aver])]}')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.1,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.show()
