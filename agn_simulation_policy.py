from __future__ import annotations
from typing import Final, List, Dict
from os.path import isdir, isfile, join
from dataclasses import dataclass
from unit_convert import UnitConvert
from math import radians
import pint
from os import listdir

_LENGTH = 'L'
_TIME = 'T'
_MASS = 'M'
_TEMPERATURE = 'K'
_ANGLE = 'A'
_ENERGY = 'ML2T-2'
_N_H_DIM = '_N_H_'


_AGN_SIMULATION_DATA_DIR_PREFIX: Final[str] = 'data'
_AGN_SIMULATION_INFO_FILE_POSSIBLE_NAMES: Final[List[str]] = [
    'info.txt', 'Info.txt']
_AGN_CLOUDS_FILE_NAME: Final[str] = 'clouds.txt'
_AGN_SIMULATION_LABEL_HINT = 'thread'

_AGN_SIMULATION_UNITS: Final[Dict[str, str]] = {
    _LENGTH: 'meters',
    _TIME: 'seconds',
    _MASS: 'kilograms',
    _TEMPERATURE: 'kelvins',
    _ENERGY: 'electronvolts',
    _ANGLE: 'degrees',
    _N_H_DIM: '1/m^2'
}

_AGN_PROCESSING_UNITS: Final[Dict[str, str]] = {
    _LENGTH: 'cm',
    _TIME: 'seconds',
    _MASS: 'grams',
    _TEMPERATURE: 'kelvin',
    _ENERGY: 'electronvolts',
    _ANGLE: 'radians',
    _N_H_DIM: '1/cm^2'
}


_AGN_SIMULATION_INFO_FILE_INTERNAL_RADIUS_KEY = "Internal Radius"
_AGN_SIMULATION_INFO_FILE_EXTERNAL_RADIUS_KEY = "External Radius"
_AGN_SIMULATION_INFO_FILE_HALF_OPENING_ANGLE_KEY = "Half Opening-angle"
_AGN_SIMULATION_INFO_FILE_COLUMN_DENSITY_KEY = "Column Density"
_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY = "Average Number(sightline) of Clouds"
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
        simulations_files_directory) if _AGN_SIMULATION_LABEL_HINT in sim_file]

    return files


@dataclass
class _AgnInfoRaw:
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
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r1, dimensionality=_LENGTH)

    def get_external_radius(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r2, dimensionality=_LENGTH)

    def get_half_opening_angle(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.theta, dimensionality=_ANGLE)

    def get_average_column_density(self) -> float:
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.nh_aver, dimensionality=_N_H_DIM)

    def get_aver_n_clouds(self):
        return self._info_raw.n_aver

    def get_volume_filling_factor(self):
        return self._info_raw.phi

    def get_n_photons(self):
        return self._info_raw.n_photons

    def get_n_clouds(self):
        return self._info_raw.n_clouds

    def get_r_clouds(self):
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.r_clouds, dimensionality=_LENGTH)

    def get_temperature_electrons(self):
        return self.__translate_from_sim_to_processing_units(value=self._info_raw.temperature_e, dimensionality=_TEMPERATURE)

    def get_other_extra_parameters(self):
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
        n_aver = int(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_AVER_N_CLOUDS_KEY])
        phi = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_FILLING_FACTOR_KEY])
        n_photons = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_N_PHOTONS_KEY])
        n_clouds = int(info_dict_raw[_AGN_SIMULATION_INFO_FILE_N_CLOUDS_KEY])
        r_clouds = float(info_dict_raw[_AGN_SIMULATION_INFO_FILE_R_CLOUDS_KEY])
        temperature_e = float(
            info_dict_raw[_AGN_SIMULATION_INFO_FILE_ELECTRONS_TEMPERATURE_KEY])
        other_parameters = []
        return _AgnInfoRaw(
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
        return (value*self.ureg[_AGN_SIMULATION_UNITS[dimensionality]]).to(self.ureg[_AGN_PROCESSING_UNITS[dimensionality]]).magnitude
