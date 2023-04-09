from __future__ import annotations
from typing import Final, List, Dict
from os.path import isdir, isfile, join
from dataclasses import dataclass
from math import radians
import pint
from os import listdir
from utils import *


_AGN_SIMULATION_DATA_DIR_PREFIX: Final[str] = 'data'
_AGN_SIMULATION_INFO_FILE_POSSIBLE_NAMES: Final[List[str]] = [
    'info.txt', 'Info.txt']
_AGN_CLOUDS_FILE_NAME: Final[str] = 'clouds.txt'
_AGN_SIMULATION_LABEL_HINT = 'thread'

AGN_SIMULATION_NAME_POL_IRON_ABUNDANCE_POS = 3
AGN_IRON_ABUNDANCE_LABEL = 'a_fe'

AGN_EFFECTIVE_LENGTHS_DIR_LABEL = 'effective_lengths'
AGN_EFFECTIVE_LENGTHS_LABEL = AGN_EFFECTIVE_LENGTHS_DIR_LABEL


def get_effective_lengths_directions_filename(angle_interval_label: str):
    return f'{AGN_EFFECTIVE_LENGTHS_DIR_LABEL}_{angle_interval_label}'


def get_effective_lengths_label_from_filename(effective_lengths_filename: str):
    return effective_lengths_filename.split(sep='_')[-1]


AGN_NH_VIEWING_DIRECTIONS_DEG: Final[Dict[str, AngularInterval]] = {
    "6075": AngularInterval(60, 15),
    "7590": AngularInterval(75, 15)
}


AGN_IRON_ABUNDANCE: Final[Dict[str, float]] = {
    "05xfe": 0.5,
    "07xfe": 0.7,
    "1xfe": 1,
    "15xfe": 1.5,
    "2xfe": 2,
}


AGN_SIMULATION_UNITS: Final[Dict[str, str]] = {
    LENGTH: 'meters',
    TIME: 'seconds',
    MASS: 'kilograms',
    TEMPERATURE: 'kelvins',
    ENERGY: 'eV',
    ANGLE: 'degrees',
    N_H_DIM: '1/m^2'
}

AGN_PROCESSING_UNITS: Final[Dict[str, str]] = {
    LENGTH: 'cm',
    TIME: 'seconds',
    MASS: 'grams',
    TEMPERATURE: 'kelvin',
    ENERGY: 'eV',
    ANGLE: 'radians',
    N_H_DIM: '1/cm^2'
}


_AGN_SIMULATION_INFO_FILE_INTERNAL_RADIUS_KEY = "Internal Radius"
_AGN_SIMULATION_INFO_FILE_EXTERNAL_RADIUS_KEY = "External Radius"
_AGN_SIMULATION_INFO_FILE_HALF_OPENING_ANGLE_KEY = "Half Opening-angle"
_AGN_SIMULATION_INFO_FILE_COLUMN_DENSITY_KEY = "Column Density"
_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY = "Average Number(sightline) of Clouds"
_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY_VARIANT2 = "Average Number(sight line) of Clouds"
_AGN_SIMULATION_INFO_FILE_FILLING_FACTOR_KEY = "Volume Filling Factor"
_AGN_SIMULATION_INFO_FILE_N_PHOTONS_KEY = "Number of Photons"
_AGN_SIMULATION_INFO_FILE_N_CLOUDS_KEY = "Number of Clouds"
_AGN_SIMULATION_INFO_FILE_R_CLOUDS_KEY = "Radius of the clouds"
_AGN_SIMULATION_INFO_FILE_ELECTRONS_TEMPERATURE_KEY = "Temperature of Electrons"


def get_info_file_path(sim_root: str) -> str:
    for possible_info_file_name in _AGN_SIMULATION_INFO_FILE_POSSIBLE_NAMES:
        if isfile((x := join(sim_root,
                             _AGN_SIMULATION_DATA_DIR_PREFIX,
                             possible_info_file_name))):
            return x
    else:
        raise FileExistsError(
            'The agn simulation info file could not be found!')


def get_clouds_file_path(sim_root: str) -> str:

    if isfile((x := join(sim_root,
                         _AGN_SIMULATION_DATA_DIR_PREFIX,
                         _AGN_CLOUDS_FILE_NAME))):
        return x
    else:
        raise FileExistsError(
            'The agn simulation clouds file could not be found!')


def get_simulation_files_list(sim_root: str) -> List[str]:

    simulations_files_directory = join(
        sim_root, _AGN_SIMULATION_DATA_DIR_PREFIX)

    files = [join(simulations_files_directory, sim_file) for sim_file in listdir(
        simulations_files_directory) if _AGN_SIMULATION_LABEL_HINT in sim_file and sim_file[-1:-4:-1] == 'txt']

    return files


@dataclass
class AgnInfoRaw:
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


class AgnSimulationPolicy:
    """This class handles the details of getting the agn simulation
    information according to the established units, format of the info
    file, etc. Its responsibility is to translate properly the info file
    and give you useful data according to the policy.

    Here the word policy means the way we save values, text, units, from simulation 
    and how to translate this data into useful data for processing the simulations.


    The idea is that if we decide to change something in way the simulation
    results are saved, this should not affect the way we process the simulations.

    Therefore this class if the bridge between simulation info and simulation processing.

    ============================

    example:

    policy = AgnSimulationPolicy(info_file='/path/to/sim_root/data/Info.txt')

    print(pol.get_internal_radius())

    ============================

    """

    def __init__(self, info_file: str):
        self._info_raw = self.__get_info_raw(info_file)
        self.ureg = pint.UnitRegistry()

    def get_internal_radius(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r1, dimensionality=LENGTH)

    def get_external_radius(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r2, dimensionality=LENGTH)

    def get_half_opening_angle(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.theta, dimensionality=ANGLE)

    def get_average_column_density(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.nh_aver, dimensionality=N_H_DIM)

    def get_aver_n_clouds(self):
        return self._info_raw.n_aver

    def get_volume_filling_factor(self):
        return self._info_raw.phi

    def get_n_photons(self):
        return self._info_raw.n_photons

    def get_n_clouds(self):
        return self._info_raw.n_clouds

    def get_r_clouds(self):
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r_clouds, dimensionality=LENGTH)

    def get_temperature_electrons(self):
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.temperature_e, dimensionality=TEMPERATURE)

    def get_other_extra_parameters(self, f: any = None):
        if f:
            return f(self._info_raw)
        else:
            return self._info_raw.other_parameters

    def __get_info_raw(self, info_file: str):
        info_dict_raw = self.__get_info_dict_raw(info_file)

        r1 = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_INTERNAL_RADIUS_KEY])
        r2 = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_EXTERNAL_RADIUS_KEY])
        theta = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_HALF_OPENING_ANGLE_KEY])
        nh_aver = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_COLUMN_DENSITY_KEY])

        try:
            n_aver = int(
                info_dict_raw[_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY])
        except KeyError as e:
            n_aver = int(
                info_dict_raw[_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY_VARIANT2])

        phi = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_FILLING_FACTOR_KEY])
        n_photons = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_N_PHOTONS_KEY])
        n_clouds = int(info_dict_raw[_AGN_SIMULATION_INFO_FILE_N_CLOUDS_KEY])
        r_clouds = float(info_dict_raw[_AGN_SIMULATION_INFO_FILE_R_CLOUDS_KEY])
        temperature_e = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_ELECTRONS_TEMPERATURE_KEY])
        other_parameters = []
        return AgnInfoRaw(
            r1=r1,
            r2=r2,
            theta=theta,
            nh_aver=nh_aver,
            n_aver=n_aver,
            phi=phi,
            n_photons=n_photons,
            n_clouds=n_clouds,
            r_clouds=r_clouds,
            temperature_e=temperature_e,
            other_parameters=other_parameters
        )

    def __get_info_dict_raw(self, info_file: str) -> Dict[str:str]:
        result = {}
        with open(info_file) as info:
            for line in info:
                key, value = line.rsplit(sep=':')
                result[key.strip()] = value.split()[0]

        return result

    def __translate_from_sim_to_processing_units(self, value, dimensionality: str):
        return (value*self.ureg[AGN_SIMULATION_UNITS[dimensionality]]).to(self.ureg[AGN_PROCESSING_UNITS[dimensionality]]).magnitude
