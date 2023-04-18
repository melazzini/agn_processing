from measurable_utils import get_edge_vs_h
from colum_density_utils import ColumnDensityGrid
from agn_processing_policy import *
from agn_simulation_policy import AGN_IRON_ABUNDANCE
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
import numpy as np
import os
from paths_in_this_machine import *
from matplotlib.pyplot import figure
from scipy.optimize import curve_fit
figure(figsize=(8, 7), dpi=120)


def fit_h_N_fit_m1(h, a, b, c):
    return a + b*np.log10(h) + c*np.log10(h)**2

def fit_h_N_fit_m2(h, a, b, c, d):
    return a + b*h**1.2 + c*h**d


g = ColumnDensityGrid(LEFT_NH, RIGHT_NH, NH_INTERVALS)

plt.grid()

ABUNDANCE_COLOR = {
    '05xfe': 'peru',
    '1xfe': 'cyan',
    '2xfe': 'blue',
}

NH_COLORS = {
    5e22: 'red',
    1e23: 'gold',
    2e23: 'brown',
    5e23: 'g',
    1e24: 'pink',
}

data_per_abundance = {}
data_per_nh = {}


for n_h in [5e22, 1e23, 2e23, 5e23, 1e24]:
    for a_fe in ['05xfe', '1xfe', '2xfe']:
        h, h_err, edge, edge_err = get_edge_vs_h(
            os.path.join(
                repo_directory, f"{g.n_intervals}_{g.left:0.2g}_{g.right:0.2g}.measurements"),
            nh_index=g.index(nh=n_h), a_fe=a_fe)
        if len(h) == 0:
            continue

        if a_fe not in data_per_abundance:
            data_per_abundance[a_fe] = [list(), list()]

        if n_h not in data_per_nh:
            data_per_nh[n_h] = [list(), list()]

        data_per_abundance[a_fe][0] += list(h)
        data_per_abundance[a_fe][1] += list(1-edge)

        data_per_nh[n_h][0] += list(h)
        data_per_nh[n_h][1] += list(1-edge)

        plt.scatter(
            h, 1-edge, edgecolors=ABUNDANCE_COLOR[a_fe], c=NH_COLORS[n_h], label=r'$N_H=$' f'{n_h:0.2g}' r'$cm^{-2}$, $A_{Fe}=$' f'{AGN_IRON_ABUNDANCE[a_fe]:0.2g}')

        plt.errorbar(h, 1-edge, edge_err, color='none',
                     ecolor='black', xerr=h_err, elinewidth=0.9)


for a_fe in ['05xfe', '1xfe', '2xfe']:
    xdata, ydata = data_per_abundance[a_fe]
    pars, _ = curve_fit(fit_h_N_fit_m1, xdata=xdata, ydata=ydata)
    x0, x1 = min(xdata), max(xdata)
    x = np.linspace(x0, x1, 100)
    plt.plot(x, fit_h_N_fit_m1(x, *pars),
             color=ABUNDANCE_COLOR[a_fe], linestyle='dashed', linewidth=1)


for n_h in [1e23, 2e23, 5e23, 1e24]:
    xdata, ydata = data_per_nh[n_h]
    pars, _ = curve_fit(fit_h_N_fit_m2, xdata=xdata, ydata=ydata, maxfev=1_000_000)
    x0, x1 = min(xdata), max(xdata)
    x = np.linspace(x0, x1, 100)
    plt.plot(x, fit_h_N_fit_m2(x, *pars),
             color=NH_COLORS[n_h], linestyle='dashed', linewidth=1)

plt.legend()
plt.xlabel('H')
plt.ylabel(r'$1-N_{Fe}$')
plt.xscale('log')
# plt.yscale('log')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.1,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.show()
