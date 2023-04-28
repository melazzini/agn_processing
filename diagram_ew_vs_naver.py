from colum_density_utils import ValueAndError, ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt
from measurable_utils import load_data_from_file, filter_data_by_nh, filter_data_by_nhaver, filter_data_by_viewing_angle, AngularInterval, filter_data_by_abundance
from paths_in_this_machine import repo_directory, MEASUREMENTS_FILEPATH
from scipy.optimize import curve_fit
from agn_art_utils import *
from matplotlib.pyplot import figure
from agn_art_utils import *
import numpy as np
from matplotlib.lines import Line2D


def fit_ew_vs_n_aver(n_aver: int, a, b, c):
    return a + b*n_aver + c*n_aver**2


figure(figsize=(8, 7), dpi=120)

plt.grid()

data = load_data_from_file(measurements_filepath=MEASUREMENTS_FILEPATH)
data = filter_data_by_nh(data=data, nh_index=DEFAULT_NH_GRID.index(nh=1e24))
data = filter_data_by_nhaver(data=data, nh_aver='24')
data = filter_data_by_abundance(data=data, a_fe='1xfe')

data_60 = filter_data_by_viewing_angle(
    data=data, alpha=AngularInterval(60, 15))
x = []
y = []
for measurement in data_60:

    n_aver = measurement.key.n_aver if measurement.key.n_aver != NUM_OF_CLOUDS_SMOOTH else 10
    x += [n_aver]
    y += [measurement.value.ew.value]
    plt.scatter(n_aver, measurement.value.ew.value, [150],
                color='blue', marker=MARKERS[measurement.key.n_aver])
    plt.errorbar(n_aver, measurement.value.ew.value,
                 measurement.value.ew.err, color='none', ecolor='black')


pars, pcov = curve_fit(fit_ew_vs_n_aver, xdata=np.array(x),
                       ydata=np.array(y), maxfev=1_000_000)


x = np.linspace(min(x), max(x), num=100)
y = fit_ew_vs_n_aver(x, *pars)

plt.plot(x, y, color='gray')


x = []
y = []
data_75 = filter_data_by_viewing_angle(
    data=data, alpha=AngularInterval(75, 15))
for measurement in data_75:

    n_aver = measurement.key.n_aver if measurement.key.n_aver != NUM_OF_CLOUDS_SMOOTH else 10
    x += [n_aver]
    y += [measurement.value.ew.value]
    plt.scatter(n_aver, measurement.value.ew.value, [150],
                color='red', marker=MARKERS[measurement.key.n_aver])
    plt.errorbar(n_aver, measurement.value.ew.value,
                 measurement.value.ew.err, color='none', ecolor='black')


pars, pcov = curve_fit(fit_ew_vs_n_aver, xdata=np.array(x),
                       ydata=np.array(y), maxfev=1_000_000)

x = np.linspace(min(x), max(x), num=100)
y = fit_ew_vs_n_aver(x, *pars)

plt.plot(x, y, color='gray')


lines = [
    Line2D([0], [0], color=color_i) for color_i in ['blue', 'red', 'gray']
]

labels = [
    r'$\alpha =$' f'{alpha}' r'$^{\circ}$' for alpha in [60, 75]
]

labels += ['fit']

plt.legend(lines, labels)

plt.xlabel(r'$<N>$')
plt.ylabel(r'$EW_{K\alpha}$ eV')
plt.title(
    r'$<N_H> = N_H = 10^{24} cm^{-2}$, $A_{Fe}=1$')
# r'$<N_H> = 5\times 10^{23}cm^{-2}$, $N_H= 10^{24} cm^{-2}$, $A_{Fe}=1$')
plt.subplots_adjust(
    top=0.95,
    bottom=0.07,
    left=0.1,
    right=0.97,
    hspace=0.2,
    wspace=0.2
)
plt.show()
