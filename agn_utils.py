from __future__ import annotations
from agn_simulation_policy import *
from functools import reduce


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
    def build_agn_simulation_info(sim_root_dir: str) -> AgnSimulationInfo:
        """This factory method builds an AgnSimulationInfo obj.

        Args:
            sim_root_dir (str): path to the simulation root directory.
        """

        info_file_path = get_info_file_path(sim_root_dir)
        policy = AgnSimulationPolicy(info_file_path)

        return AgnSimulationInfo(
            sim_root_dir=sim_root_dir,
            file_path=info_file_path,
            clouds_file_path=get_clouds_file_path(sim_root_dir),
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
            other_parameters=policy.get_other_extra_parameters(),
            simulation_files=get_simulation_files_list(sim_root_dir)
        )
