from colum_density_utils import ValueAndError, ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import Dict, List, Tuple, Final
from agn_simulation_policy import AGN_NH_AVERAGE
from measurable_utils import parse_measurement, get_shoulder_vs_nhaver
from measurements import MeasurementsKey, MeasurementsValue, AngularInterval
from paths_in_this_machine import repo_directory
import os
from matplotlib.pyplot import figure

figure(figsize=(8, 7), dpi=120)

NUM_OF_CLOUDS_SMOOTH = -1

NH_COLORS = {
    '22': 'red',
    '522': 'blue',
    '23': 'gold',
    '223': 'brown',
    '523': 'g',
    '24': 'pink',
}

MARKERS: Final[Dict[int, str]] = {1: '.', 2: '<', 3: '>',
                                  4: '^', 5: '*', 6: 's', 8: 'v', 10: 'p',
                                  NUM_OF_CLOUDS_SMOOTH: 'o', }
"""
Markers to plot/label agn spectrum characteristics,
considering the number of clouds corresponding to
the given spectrum component.
"""


COL_DENSITY_LABELS = {
    '522': r'$5\times10^{22} cm^{-2}$',
    '23': r'$10^{23} cm^{-2}$',
    '223': r'$2\times10^{23} cm^{-2}$',
    '323': r'$3\times10^{23} cm^{-2}$',
    '523': r'$5\times10^{23} cm^{-2}$',
    '24': r'$10^{24} cm^{-2}$',
    '224': r'$2\times10^{24} cm^{-2}$',
}


g = ColumnDensityGrid(left_nh=LEFT_NH, right_nh=RIGHT_NH,
                      n_intervals=NH_INTERVALS)


def get_shoulder_vs_ew(measurements_filepath: str, nh_id: int, a_fe: str) -> Dict[MeasurementsKey, Tuple[ValueAndError, ValueAndError]]:
    data: Dict[MeasurementsKey, Tuple[ValueAndError, ValueAndError]] = {}

    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)

            if nh_id != key.nh_index or a_fe != key.a_fe:
                continue

            data[key] = (value.ew, value.shoulder)

    return data


data: Dict[MeasurementsKey, Tuple[ValueAndError, ValueAndError]] = get_shoulder_vs_ew(
    os.path.join(repo_directory, f"{g.n_intervals}_{g.left:0.2g}_{g.right:0.2g}_{HV_N_INTERVALS}.measurements"), nh_id=g.index(1e24), a_fe='1xfe')

colors_used = []
nha_used = []

for key in data:

    if key.alpha == AngularInterval(60, 15):

        if data[key][1].err / data[key][1].value > 0.15:
            continue

        if NH_COLORS[key.nh_aver] not in colors_used:

            colors_used += [NH_COLORS[key.nh_aver]]
            nha_used += [key.nh_aver]

        plt.scatter(data[key][0].value, data[key][1].value, [
                    150], marker=MARKERS[key.n_aver], c=NH_COLORS[key.nh_aver])

        plt.errorbar(data[key][0].value, data[key][1].value,
                     yerr=data[key][1].err, xerr=data[key][0].err, color='none', ecolor='black', linewidth=0.9)

    elif key.alpha == AngularInterval(75, 15):

        if data[key][1].err / data[key][1].value > 0.15:
            continue

        plt.scatter(data[key][0].value, data[key][1].value, [
                    150], marker=MARKERS[key.n_aver], c='none', edgecolors=NH_COLORS[key.nh_aver], linewidths=1.5)

        plt.errorbar(data[key][0].value, data[key][1].value,
                     yerr=data[key][1].err, xerr=data[key][0].err, color='none', ecolor='black', linewidth=0.9)


lines = [
    Line2D([0], [0], color=color_i) for color_i in colors_used
]

labels = [
    r'$<N_H> =$' f'{COL_DENSITY_LABELS[nha_i]}' for nha_i in nha_used
]


# lines += [
#     Line2D([0], [0], markeredgecolor='black', marker=MARKERS[n_i], markersize=10, color='none') for n_i in MARKERS if n_i != 1
# ]

# labels += [
#     r'$<N> =$' f'{n_i if n_i!=NUM_OF_CLOUDS_SMOOTH else "smooth"}' for n_i in MARKERS if n_i != 1
# ]

plt.legend(lines, labels)

# plt.xlim(50,380)
# plt.ylim(0.02,0.25)

plt.title(
    r'$N_H=10^{24}cm^{-2}$,  $A_{Fe}=$' f'{1}')
plt.subplots_adjust(
    top=0.94,
    bottom=0.10,
    left=0.11,
    right=0.98,
    hspace=0.2,
    wspace=0.2
)
plt.xlabel(r'$EW_{K\alpha}, eV$')
plt.ylabel(r'$C_{K\alpha}$')
plt.show()
