"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from utils import AngularInterval
from paths_in_this_machine import root_simulations_directory
from typing import Iterable
from agn_utils import AgnSimulationInfo
import os

nh_aver = 1e23
n_aver = 3
a_fe = 1
alpha = AngularInterval(60, 15)


def simulations_root_dir(nh_aver: float, n_aver: int, a_fe: float, alpha: AngularInterval) -> str:
    """This function returns the root simulations directory for the given parameters.

    Args:
        nh_aver (float): average column density
        n_aver (int): average number of clouds on the line of sight
        a_fe (float): iron abundance
        alpha (AngularInterval): viewing angular interval

    Returns:
        str: the path to the simulations root directory
    """
    return root_simulations_directory


sims_root_dir = simulations_root_dir(
    nh_aver=nh_aver, n_aver=n_aver, a_fe=a_fe, alpha=alpha)


def get_simulations(sims_root_dir: str, nh_aver: float, n_aver: int, a_fe: float) -> Iterable[AgnSimulationInfo]:

    for item in os.listdir(sims_root_dir):

        if "spectral_data" == item or "past" == item:
            continue

        sim_path = os.path.join(sims_root_dir, item)

        s = AgnSimulationInfo.build_agn_simulation_info(sim_path,lambda x: ["yubadoo!","wow", 1,2,3])

        print(s)
        break

    return None


get_simulations(sims_root_dir=sims_root_dir,
                nh_aver=nh_aver, n_aver=n_aver, a_fe=a_fe)
