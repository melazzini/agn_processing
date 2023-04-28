from measurable_utils import get_edge_vs_h, parse_measurement
from colum_density_utils import ColumnDensityGrid, DEFAULT_NH_GRID
from agn_processing_policy import *
from agn_simulation_policy import AGN_IRON_ABUNDANCE, AGN_NH_AVERAGE
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List, Final
import numpy as np
import os
from paths_in_this_machine import *
from matplotlib.pyplot import figure
from measurable_utils import AngularInterval, load_data_from_file, filter_data_by_nh, filter_data_by_viewing_angle
from paths_in_this_machine import MEASUREMENTS_FILEPATH
from agn_art_utils import *
import random
figure(figsize=(8, 7), dpi=120)


def fit_h_N_fit_m1(h, a, b, c):
    return a + b*np.log10(h) + c*np.log10(h)**2


def fit_h_N_fit_m2(h, a, b, c, d):
    return a + b*h**1.2 + c*h**d


plt.grid()

data = load_data_from_file(measurements_filepath=MEASUREMENTS_FILEPATH)
data = filter_data_by_nh(data=data, nh_index=DEFAULT_NH_GRID.index(nh=1e23))
data_60 = filter_data_by_viewing_angle(
    data=data, alpha=AngularInterval(60, 15))

for measurement in data_60:
    a_fe = AGN_IRON_ABUNDANCE[measurement.key.a_fe]
    h = measurement.value.h

    x_rand_possition = a_fe*(1+0.1*(0.5-random.random()))

    plt.scatter(x_rand_possition, h.value, [150],
                color=NH_COLORS[DEFAULT_NH_GRID.index(
                    nh=float(AGN_NH_AVERAGE[measurement.key.nh_aver]))],
                marker=MARKERS[measurement.key.n_aver])

    plt.errorbar(x_rand_possition, h.value, h.err, color='none',
                 ecolor='black', elinewidth=0.9)

data_75 = filter_data_by_viewing_angle(
    data=data, alpha=AngularInterval(75, 15))

for measurement in data_75:
    a_fe = AGN_IRON_ABUNDANCE[measurement.key.a_fe]
    h = measurement.value.h
    x_rand_possition = a_fe*(1+0.1*(0.5-random.random()))
    plt.scatter(x_rand_possition, h.value, [150],
                color='none',
                edgecolor=NH_COLORS[DEFAULT_NH_GRID.index(
                    nh=float(AGN_NH_AVERAGE[measurement.key.nh_aver]))],
                marker=MARKERS[measurement.key.n_aver])

    plt.errorbar(x_rand_possition, h.value, h.err, color='none',
                 ecolor='black', elinewidth=0.9)


plt.legend()
plt.xlabel(r'$C_{K\alpha}$')
plt.ylabel(r'$H$')
# plt.xscale('log')
# plt.yscale('functionlog')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.1,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.show()
