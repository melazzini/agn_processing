from colum_density_utils import ValueAndError, ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from agn_simulation_policy import AGN_NH_AVERAGE, AGN_IRON_ABUNDANCE
from measurable_utils import get_shoulder_vs_nhaver
from paths_in_this_machine import repo_directory, MEASUREMENTS_FILEPATH
import os
from agn_art_utils import *
import random
from scipy.optimize import curve_fit
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.pyplot import figure
figure(figsize=(14, 7), dpi=120)


def fit_function(nh_aver, a, b, c, d, e):
    x = np.log10(nh_aver)
    # x = 1/x**d
    return a + b*x**e + c*x**d
    # return a + b*x**2 + c*x**1 + d*x**e


plt.grid()

data: Dict[Tuple[str, str, bool, int], List[ValueAndError]] = get_shoulder_vs_nhaver(
    os.path.join(repo_directory, MEASUREMENTS_FILEPATH))

x = []
y = []

for key in data:

    nh_key = key[0]
    a_fe = key[1]
    is_alpha_75 = key[2]
    n_aver = key[3]

    for shoulder in data[key]:

        if nh_key != '22' and nh_key != '222':
            if (shoulder.value <= 0 or shoulder.err/shoulder.value > 0.1):
                continue

        if nh_key == '822':
            continue

        factor = (1+0.15*(0.5-random.random()))

        true_x_pos = AGN_NH_AVERAGE[nh_key]
        x += [true_x_pos]
        y += [shoulder.value]
        x_pos = true_x_pos*factor

        plt.scatter(x_pos, shoulder.value, [150],
                    edgecolor=NH_COLORS[DEFAULT_NH_GRID.index(nh=AGN_NH_AVERAGE[nh_key])], color='none', marker=MARKERS[n_aver])

        # if is_alpha_75:
        #     plt.errorbar(x_pos, shoulder.value,
        #                  shoulder.err, xerr=true_x_pos*(1-factor), color='none', ecolor=ABUNDANCE_COLOR[a_fe], linewidth=0.9)
        # else:
        plt.errorbar(x_pos, shoulder.value,
                     shoulder.err, color='none', ecolor=ABUNDANCE_COLOR[a_fe], linewidth=0.9)


pars, _ = curve_fit(fit_function, np.array(x), np.array(y), maxfev=1_000_000)

x = np.linspace(min(x), max(x), num=1000)
y = fit_function(x, *pars)
plt.plot(x, y, color='black')


lines = [
    Line2D([0], [0], color=NH_COLORS[index]) for index in NH_COLORS
]

labels = [
    r'$<N_H> = $' f'{NH_LABELS[index]}' for index in NH_COLORS
]

lines += [
    Line2D([0], [0], color=ABUNDANCE_COLOR[key]) for key in ABUNDANCE_COLOR
]

labels += [
    r'$A_{Fe} = $' f'{AGN_IRON_ABUNDANCE[key]}' for key in AGN_IRON_ABUNDANCE
]

lines += [
    Line2D([0], [0], markeredgecolor='black', marker=MARKERS[n_i], markersize=10, color='none') for n_i in MARKERS if n_i != 1
]

labels += [
    r'$<N> =$' f'{n_i if n_i!=NUM_OF_CLOUDS_SMOOTH else "smooth"}' for n_i in MARKERS if n_i != 1
]

plt.legend(lines, labels)


plt.xscale('log')

plt.xlabel(r'$<N_H>$')
plt.ylabel(r'$C_{K\alpha}$')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.06,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)

plt.show()
