"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from utils import AngularInterval
from paths_in_this_machine import root_simulations_directory
from typing import Final, Dict, List
from agn_utils import get_simulations_in_sims_root_dir, AgnSimulationInfo, get_total_n_photons
import os
from functools import reduce


nh_aver = 2e23
n_aver = 4
a_fe = 0.5
alpha = AngularInterval(60, 15)


def simulations_root_dir(nh_aver: float) -> str:
    """This function returns the root simulations directory for the given parameters.

    Args:
        nh_aver (float): average column density

    Returns:
        str: the path to the simulations root directory
    """

    # TODO:

    if nh_aver != 2e23:
        raise ValueError('the nh_value is not valid at the moment!')

    return root_simulations_directory


sims_root_dir = simulations_root_dir(nh_aver=nh_aver)

simulations = get_simulations_in_sims_root_dir(sims_root_dir=sims_root_dir,
                                               n_aver=n_aver, a_fe=a_fe)

n_photons = get_total_n_photons(simulations=simulations)
