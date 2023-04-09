"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from utils import AngularInterval
from paths_in_this_machine import root_simulations_directory
from typing import Final, Dict, List
from agn_utils import get_simulations_in_sims_root_dir, AgnSimulationInfo, get_total_n_photons, AGN_EFFECTIVE_LENGTHS_LABEL, AGN_NH_VIEWING_DIRECTIONS_DEG
import os
import numpy as np


nh_aver = 5e23
n_aver = 2
a_fe = 1
alpha = AngularInterval(60, 15)


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


sims_root_dir = simulations_root_dir(nh_aver=nh_aver)

simulations = get_simulations_in_sims_root_dir(sims_root_dir=sims_root_dir,
                                               n_aver=n_aver, a_fe=a_fe)

n_photons = get_total_n_photons(simulations=simulations)


def get_direction_filepaths(simulations: List[AgnSimulationInfo], alpha: AngularInterval) -> List[str]:
    direction_files = []

    for sim in simulations:
        for viewing_angle_key in (x := sim.other_parameters[AGN_EFFECTIVE_LENGTHS_LABEL]):
            if AGN_NH_VIEWING_DIRECTIONS_DEG[viewing_angle_key] == alpha:
                direction_files += [x[viewing_angle_key]]

    return direction_files


def get_directions(simulations: List[AgnSimulationInfo], alpha: AngularInterval) -> np.ndarray:

    files = get_direction_filepaths(simulations=simulations, alpha=alpha)
    directions = []
    for file_i in files:
        directions += list(np.loadtxt(file_i))

    return np.array(directions)


print(len(get_directions(simulations=simulations, alpha=alpha)), sep='\n')
