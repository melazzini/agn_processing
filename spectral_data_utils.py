"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from utils import AngularInterval
from paths_in_this_machine import root_simulations_directory
from typing import Final, Dict, List
from agn_utils import *
import os
import numpy as np
from colum_density_utils import ColumnDensityGrid
from agn_processing_policy import *


def simulations_root_dir(nh_aver: float) -> str:
    """This function returns the root simulations directory for the given parameters.

    Args:
        nh_aver (float): average column density

    Returns:
        str: the path to the simulations root directory
    """

    # TODO:

    if nh_aver != 5e23:
        raise ValueError('the nh_value is not valid at the moment!')

    return root_simulations_directory


def get_spectra_directory_name(alpha: AngularInterval, grid: ColumnDensityGrid) -> str:

    for label in AGN_VIEWING_DIRECTIONS_DEG:
        if AGN_VIEWING_DIRECTIONS_DEG[label] == alpha:
            return f'THETA_{label}_nh_grid_{grid.n_intervals}_{grid.left:0.2g}_{grid.right:0.2g}'


def get_spectra_directories(simulations: List[AgnSimulationInfo], alpha: AngularInterval, grid: ColumnDensityGrid):

    spectra_dirs = []

    for simulation_i in simulations:
        sim_dir = simulation_i.sim_root_dir

        spectra_dir = os.path.join(sim_dir,
                                   get_spectra_directory_name(alpha=alpha, grid=grid))

        if os.path.exists(spectra_dir):
            spectra_dirs += [spectra_dir]

    return spectra_dirs

