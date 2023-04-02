"""
==========================
example 01:

from photon_register_policy import PhotonRawInfo

photonRawInfo = PhotonRawInfo.build_photon_raw_info(raw_info='6404.7 0.1 0.1 3 13 1 1e13 2 1e12 1e12 1e12 1e9')

print(photonRawInfo)

===========================

"""


from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Final, Dict
from utils import *
import pint

PHOTON_TYPES_LABELS: Final[Dict[str, float]] = {
    '0': 'SOURCE',  # THE PHOTON COMES FROM THE SOURCE AND DID NOT INTERSECT ANY CLOUD OR MATTER IN THE TORUS
    # THE PHOTON INTERSECTED THE TORUS CLOUDS/MATTER BUT IT DID NOT INTERACTED
    '1': 'NO_INTERACTIONS',
    '2': 'SCATTERING',  # THE PHOTON INTERACTED WITH THE TORUS BY COMPTON SCATTING
    '3': 'FLUORESCENT',  # THIS IS A FLUORESCENT PHOTON
}


_PHOTON_SIMULATION_UNITS: Final[Dict[str, str]] = {
    LENGTH: 'meters',
    TIME: 'seconds',
    MASS: 'kilograms',
    TEMPERATURE: 'kelvins',
    ENERGY: 'eV',
    ANGLE: 'radians',
    N_H_DIM: '1/m^2'
}

_PHOTON_PROCESSING_UNITS: Final[Dict[str, str]] = {
    LENGTH: 'cm',
    TIME: 'seconds',
    MASS: 'grams',
    TEMPERATURE: 'kelvin',
    ENERGY: 'eV',
    ANGLE: 'radians',
    N_H_DIM: '1/cm^2'
}


FLUORESCENT_LINES_LABELS: Final[Dict[str, float]] = {
    '0': 'NONE',
    '1': 'CKalpha',
    '2': 'NKalpha',
    '3': 'OKalpha',
    '4': 'NeKalpha',
    '5': 'NaKalpha',
    '6': 'MgKalpha',
    '7': 'AlKalpha',
    '8': 'SiKalpha',
    '9': 'SKalpha',
    '10': 'ArKalpha',
    '11': 'CaKalpha',
    '12': 'CrKalpha',
    '13': 'FeKalpha',
    '14': 'NiKalpha',
    '15': 'UNKNOWN',
}


def _photon_file_line_interpretation(line: str):
    items = line.split()

    if len(items) == 7:
        hv_str, theta_str, phi_str, photon_type_str, line_str, n_clouds_str, effective_length_str = items
        n_scatterings_str = '-1'
        total_path_str = '-1'
        x_str = y_str = z_str = '-1'

    elif len(items) == 12:
        hv_str, theta_str, phi_str, photon_type_str, line_str, n_scatterings_str, total_path_str, n_clouds_str, x_str, y_str, z_str, effective_length_str = items
    else:
        raise ValueError(
            f'The line: "{line}" cannot be interpreted as a simulation photon information.')

    return hv_str, theta_str, phi_str, photon_type_str, line_str, n_scatterings_str, total_path_str, n_clouds_str, x_str, y_str, z_str, effective_length_str


class PhotonType:

    def __init__(self, type_label: str):

        if type_label in PHOTON_TYPES_LABELS:
            self.type_label = type_label
        else:
            raise ValueError(f"The photon type {type_label} is inappropriate!")

    def __str__(self) -> str:
        return PHOTON_TYPES_LABELS[self.type_label]


class FluorescentLine:

    def __init__(self, line_label: str):

        if line_label in FLUORESCENT_LINES_LABELS:
            self.line_label = line_label
        else:
            raise ValueError(f"The photon line {line_label} is inappropriate!")

    def __str__(self) -> str:
        return FLUORESCENT_LINES_LABELS[self.line_label]


class AgnPhotonUnitsPolicy(UnitsPolicy):

    def __init__(self):
        self.ureg = pint.UnitRegistry()

    def translate_energy(self, value: float) -> float:
        # self.__translate_from_sim_to_processing_units(value=value, dimensionality=ENERGY)
        return value

    def translate_length(self, value: float):
        # self.__translate_from_sim_to_processing_units(value=value, dimensionality=LENGTH)
        return value*100

    def translate_angle(self, value: float):
        # self.__translate_from_sim_to_processing_units(value=value, dimensionality=ANGLE)
        return value

    def __translate_from_sim_to_processing_units(self, value, dimensionality: str):
        return (value*self.ureg[_PHOTON_SIMULATION_UNITS[dimensionality]]).to(self.ureg[_PHOTON_PROCESSING_UNITS[dimensionality]]).magnitude


@dataclass
class PhotonRawInfo:
    """
    This class represents the information of a 
    registered-from-simulation photon.

    photonRawInfo = PhotonRawInfo(
    hv=6404.7,
    theta=0.1,
    phi=0.2,
    photon_type=PhotonType('1'),
    line=FluorescentLine('13'),
    n_scatterings=1,
    total_path=1e12,
    n_clouds=3,
    escape_pos=np.array([1e10, 1e10, 1e10]),
    effective_length=1e8,
    )
    """

    hv: float
    """the energy of the photon in eV
    """

    theta: float
    """theta polar angle
    """

    phi: float
    """angle between the oz -> r
    """

    photon_type: PhotonType

    line: FluorescentLine

    n_scatterings: int
    """number of compton scatterings
    """
    total_path: float
    """total path length that the photon
    traveled inside the torus before it was registered
    """

    n_clouds: int
    """number of clouds on the photon's escape line
    """

    escape_pos: np.ndarray
    """position where the photon was registered
    """

    effective_length: float
    """the length inside the clouds intersected
    by the photon's escape line
    """

    photon_line_interpretation_policy = _photon_file_line_interpretation

    @staticmethod
    def build_photon_raw_info(raw_info: str) -> PhotonRawInfo:
        hv_str, theta_str, phi_str, photon_type_str, line_str, n_scatterings_str, total_path_str, n_clouds_str, x_str, y_str, z_str, effective_length_str = PhotonRawInfo.photon_line_interpretation_policy(
            raw_info)

        return PhotonRawInfo(
            hv=float(hv_str),
            theta=float(theta_str),
            phi=float(phi_str),
            photon_type=PhotonType(type_label=photon_type_str),
            line=FluorescentLine(line_label=line_str),
            n_scatterings=int(n_scatterings_str),
            total_path=float(total_path_str),
            n_clouds=int(n_clouds_str),
            escape_pos=np.array([float(x_str), float(y_str), float(z_str)]),
            effective_length=float(effective_length_str)
        )

    def __str__(self) -> str:
        return f'hv                 : {self.hv:>15}\n'\
               f"theta              : {self.theta:>15}\n"\
               f"phi                : {self.phi:>15}\n"\
               f"type               : {str(self.photon_type):>15}\n"\
               f"line               : {str(self.line):>15}\n"\
               f"n_scatterings      : {self.n_scatterings:>15}\n"\
               f"total_path         : {self.total_path:>15}\n"\
               f"n_clouds           : {self.n_clouds:>15}\n"\
               f"escape x           : {self.escape_pos[0]:>15}\n"\
               f"escape y           : {self.escape_pos[1]:>15}\n"\
               f"escape z           : {self.escape_pos[2]:>15}\n"\
               f"effective_length   : {self.effective_length:>15}\n"


@dataclass
class PhotonInfo:
    """
    This class represents the photon information
    according to the given policy.
    """

    hv: float
    """the energy of the photon
    """

    theta: float
    """theta polar angle
    """

    phi: float
    """angle between the oz -> r
    """

    photon_type: PhotonType

    line: FluorescentLine

    n_scatterings: int
    """number of compton scatterings
    """
    total_path: float
    """total path length that the photon
    traveled inside the torus before it was registered
    """

    n_clouds: int
    """number of clouds on the photon's escape line
    """

    escape_pos: np.ndarray
    """position where the photon was registered
    """

    effective_length: float
    """the length inside the clouds intersected
    by the photon's escape line
    """

    def effective_column_density(self, hydrogen_concentration: float) -> float:
        """Get the Column Density on the photons escape line

        Args:
            hydrogen_concentration (float): Concentration of hydrogen in matter

        Returns:
            float: The column density of the photon's escape line
        """
        return hydrogen_concentration*self.effective_length

    @staticmethod
    def build_photon_info(raw_info: str, policy: UnitsPolicy) -> PhotonRawInfo:

        photon_raw_info = PhotonRawInfo.build_photon_raw_info(raw_info)

        return PhotonInfo(
            hv=policy.translate_energy(photon_raw_info.hv),
            theta=policy.translate_angle(photon_raw_info.theta),
            phi=policy.translate_angle(photon_raw_info.phi),
            photon_type=photon_raw_info.photon_type,
            line=photon_raw_info.line,
            n_scatterings=photon_raw_info.n_scatterings,
            total_path=photon_raw_info.total_path,
            n_clouds=photon_raw_info.n_clouds,
            escape_pos=np.array([
                policy.translate_length(photon_raw_info.escape_pos[0]),
                policy.translate_length(photon_raw_info.escape_pos[1]),
                policy.translate_length(photon_raw_info.escape_pos[2]),
            ]),
            effective_length=policy.translate_length(
                photon_raw_info.effective_length)
        )

    def __str__(self) -> str:
        return f'hv                 : {self.hv:>15}\n'\
               f"theta              : {self.theta:>15}\n"\
               f"phi                : {self.phi:>15}\n"\
               f"type               : {str(self.photon_type):>15}\n"\
               f"line               : {str(self.line):>15}\n"\
               f"n_scatterings      : {self.n_scatterings:>15}\n"\
               f"total_path         : {self.total_path:>15}\n"\
               f"n_clouds           : {self.n_clouds:>15}\n"\
               f"escape x           : {self.escape_pos[0]:>15}\n"\
               f"escape y           : {self.escape_pos[1]:>15}\n"\
               f"escape z           : {self.escape_pos[2]:>15}\n"\
               f"effective_length   : {self.effective_length:>15}\n"
