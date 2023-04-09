from __future__ import annotations
from agn_simulation_policy import *
from functools import reduce
import numpy as np
from utils import *
from paths_in_this_machine import AGN_SOURCE_DATA_STORAGE_DIR
import os
from typing import Iterable, Dict

AGN_SOURCE_DATA_STORAGE_PREFIX: Final[str] = AGN_SOURCE_DATA_STORAGE_DIR


@dataclass
class AgnSimulationInfo:
    """

    This class represents all the necessary information
    to process the agn simulation data.

    You use this class to get the data to process each 
    simulation/simulation-directory.

    You don't need to create an instance yourself, use
    the factory method instead!

    ==============================

    example:

    print(AgnSimulationInfo.build_agn_simulation_info('/path/to/sim/root/dir'))

    ==============================

    """

    sim_root_dir: str
    """Full path to the simulation root directory.
    """

    file_path: str
    """Full path to the AGN Simulation file.
    """

    clouds_file_path: str
    """Full path to the file of the cloud positions used
    for the current simulation.
    """

    r1: float
    """Internal torus radius.
    """

    r2: float
    """External torus radius.
    """

    theta: float
    """Half opening angle of the torus.
    """

    nh_aver: float
    """Average column density of the torus.
    """

    n_aver: int
    """Average number of clouds on the line of sight.
    """

    phi: float
    """Volume filling factor.
    """

    n_photons: float
    """Number of photons used in the simulation, which entered
    the torus.
    """

    n_clouds: int
    """Number of clouds in the torus.
    """

    r_clouds: float
    """Radius of the clouds in the torus.
    """

    temperature_e: float
    """Temperature of the electrons in matter.
    """

    other_parameters: list
    """Other optional parameters that we may add in the future.
    """

    simulation_files: List[str]
    """Paths to the simulation files.
    """

    is_smooth: bool
    """
    This is a convenient utility for processing the simulation
    in case it is a smooth torus agn.
    
    We define smooth torus as:
    
        n_clouds==n_aver==r_clouds==0
        
        
    We don't show this information in the __str__() magic because
    it is redundant.
    """

    def _is_smooth(p: AgnSimulationPolicy):
        return p.get_aver_n_clouds() == p.get_n_clouds() == p.get_r_clouds() == 0

    def __str__(self):
        sim_metadata = f'Simulation root directory: {self.sim_root_dir}\n'\
            f'Info file path           : {self.file_path}\n'\
            f'Clouds file path         : {self.clouds_file_path}\n'\
            f'Torus internal radius    : {self.r1:0.3g}\n'\
            f'Torus external radius    : {self.r2:0.3g}\n'\
            f'Half opening angle       : {self.theta:0.3g}\n'\
            f'Average column density   : {self.nh_aver:0.3g}\n'\
            f'Average num of clouds    : {self.n_aver}\n'\
            f'Volume filling factor    : {self.phi}\n'\
            f'Number of photons        : {self.n_photons:0.3g}\n'\
            f'Number of clouds         : {self.n_clouds}\n'\
            f'Radius of the clouds     : {self.r_clouds:0.3g}\n'\
            f'Electron temperature     : {self.temperature_e:0.3g}\n'\
            f'Other params             : {self.other_parameters}\n'

        files = ['Simulation files:\n'] + \
            [f'{file_i}\n' for file_i in self.simulation_files[:-1]]
        files += [self.simulation_files[-1]]

        return sim_metadata + reduce(lambda x, y: x+y, files)

    @staticmethod
    def build_agn_simulation_info(sim_root_dir: str, f: any = None) -> AgnSimulationInfo:
        """This factory method builds an AgnSimulationInfo obj.

        Args:
            sim_root_dir (str): path to the simulation root directory.
        """

        info_file_path = get_info_file_path(sim_root_dir)
        policy = AgnSimulationPolicy(info_file_path)
        is_smooth = AgnSimulationInfo._is_smooth(policy)

        return AgnSimulationInfo(
            sim_root_dir=sim_root_dir,
            file_path=info_file_path,
            clouds_file_path=get_clouds_file_path(
                sim_root_dir) if not is_smooth else "",
            r1=policy.get_internal_radius(),
            r2=policy.get_external_radius(),
            theta=policy.get_half_opening_angle(),
            nh_aver=policy.get_average_column_density(),
            n_aver=policy.get_aver_n_clouds(),
            phi=policy.get_volume_filling_factor(),
            n_photons=policy.get_n_photons(),
            n_clouds=policy.get_n_clouds(),
            r_clouds=policy.get_r_clouds(),
            temperature_e=policy.get_temperature_electrons(),
            other_parameters=policy.get_other_extra_parameters(f=f),
            simulation_files=get_simulation_files_list(sim_root_dir),
            is_smooth=is_smooth
        )


def translate_zenit(zenith_angular_interval: AngularInterval) -> AngularInterval:
    """You pass it an angular interval seen from the oz axis
    and it gives you the corresponding angular interval
    but seen from the oxy plane.

    Args:
        zenith_angular_interval (AngularInterval): angular interval seen from the oz axis

    Returns:
        AngularInterval: angular interval seen from the oxy plane
    """

    beg = np.pi/2 - zenith_angular_interval.end
    return AngularInterval(beg=beg, length=zenith_angular_interval.length)


def agn_solid_angle(theta: AngularInterval) -> float:
    """Returns the doubled solid angle for
    the corresponding agn viewing angular interval

    Args:
        theta (AngularInterval) 

    Returns:
        float: the solid angle
    """
    solid_angle_up = solid_angle(theta.beg)
    solid_angle_base = solid_angle(theta.beg+theta.length)
    return 2*(solid_angle_base - solid_angle_up)


def get_iron_abundance_from_sim_name(simulation_name: str) -> float:
    """From the simulation name like 23_3_03_1xfe_... it gets
    the iron abundance (1 in this example).

    Args:
        simulation_name (str): just the name of the simulation directory, not the full path!

    Returns:
        float: abundance of iron
    """

    code = simulation_name.split(
        sep='_')[AGN_SIMULATION_NAME_POL_IRON_ABUNDANCE_POS]

    return AGN_IRON_ABUNDANCE[code]


def get_angle_effective_lengths_map(effective_lengths_dir: str) -> Dict[str, str]:
    """This returns the {angle_lbl->effective_lengths_filepath}

    Args:
        effective_lengths_dir (str): where to find the effective_lengths files

    Returns:
        Dict[str, str]: {angle_lbl->effective_lengths_filepath}
    """

    the_map = {}
    for effective_lengths_filename_i in os.listdir(effective_lengths_dir):
        the_map[get_effective_lengths_label_from_filename(
            effective_lengths_filename=effective_lengths_filename_i)] = os.path.join(effective_lengths_dir, effective_lengths_filename_i)

    return the_map


def get_simulations_in_sims_root_dir(sims_root_dir: str, n_aver: int, a_fe: float) -> List[AgnSimulationInfo]:
    """From a simulations root directory it returns the simulations that corresponds to the given
    number of clouds on average and the given Iron abundance.

    This function asumes that the simulations in the given root dir
    are all of the same (known by the caller) average column density.

    Args:
        sims_root_dir (str): the simulations root directory
        n_aver (int): n_aver of clouds
        a_fe (float): iron abundance

    Returns:
        List[AgnSimulationInfo]: the corresponding simulations
    """

    simulations: List[AgnSimulationInfo] = []

    for sim_name in os.listdir(sims_root_dir):

        if "spectral_data" == sim_name or "past" == sim_name:
            continue

        sim_path = os.path.join(sims_root_dir, sim_name)

        effective_lengths_directory = os.path.join(
            sim_path, AGN_EFFECTIVE_LENGTHS_DIR_LABEL)

        if not os.path.exists(effective_lengths_directory):
            raise ValueError(
                f'the effective lengths directory for {sim_path} doesn\'t exist!')

        effective_lengths_map = get_angle_effective_lengths_map(
            effective_lengths_dir=effective_lengths_directory)

        s = AgnSimulationInfo.build_agn_simulation_info(
            sim_path, lambda x: {AGN_IRON_ABUNDANCE_LABEL: get_iron_abundance_from_sim_name(simulation_name=sim_name), AGN_EFFECTIVE_LENGTHS_LABEL: effective_lengths_map})

        if s.other_parameters[AGN_IRON_ABUNDANCE_LABEL] == a_fe and s.n_aver == n_aver:
            simulations += [s]

    return simulations


def get_total_n_photons(simulations: Iterable[AgnSimulationInfo]) -> float:
    return sum(s.n_photons for s in simulations)


def get_direction_filepaths(simulations: List[AgnSimulationInfo], alpha: AngularInterval) -> List[str]:
    direction_files = []

    for sim in simulations:
        for viewing_angle_key in (x := sim.other_parameters[AGN_EFFECTIVE_LENGTHS_LABEL]):
            if AGN_VIEWING_DIRECTIONS_DEG[viewing_angle_key] == alpha:
                direction_files += [x[viewing_angle_key]]

    return direction_files