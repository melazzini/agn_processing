from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Final, Dict

PHOTON_TYPES_LABELS: Final[Dict[str, float]] = {
    '0': 'SOURCE',  # THE PHOTON COMES FROM THE SOURCE AND DID NOT INTERSECT ANY CLOUD OR MATTER IN THE TORUS
    '1': 'NO_INTERACTIONS',# THE PHOTON INTERSECTED THE TORUS CLOUDS/MATTER BUT IT DID NOT INTERACTED
    '2': 'SCATTERING',  # THE PHOTON INTERACTED WITH THE TORUS BY COMPTON SCATTING
    '3': 'FLUORESCENT',  # THIS IS A FLUORESCENT PHOTON
}


FLUORESCENT_LINES_LABELS: Final[Dict[str, float]] = {
    '0 ': 'NONE    ',
    '1 ': 'CKalpha ',
    '2 ': 'NKalpha ',
    '3 ': 'OKalpha ',
    '4 ': 'NeKalpha',
    '5 ': 'NaKalpha',
    '6 ': 'MgKalpha',
    '7 ': 'AlKalpha',
    '8 ': 'SiKalpha',
    '9 ': 'SKalpha ',
    '10': 'ArKalpha',
    '11': 'CaKalpha',
    '12': 'CrKalpha',
    '13': 'FeKalpha',
    '14': 'NiKalpha',
    '15': 'UNKNOWN ',
}


class PhotonType:

    def __init__(self, type_label: str):

        if type_label in PHOTON_TYPES_LABELS:
            self.type_label = type_label
        else:
            raise ValueError(f"The photon type {type_label} is inappropriate!")


class FluorescentLine:

    def __init__(self, line_label: str):

        if line_label in FLUORESCENT_LINES_LABELS:
            self.line_label = line_label
        else:
            raise ValueError(f"The photon line {line_label} is inappropriate!")


@dataclass
class PhotonRawInfo:
    """
    This class represents the information of a 
    registered-from-simulation photon.
    
    photonRawInfo = PhotonRawInfo(
    hv=6404.7,
    theta=0.1,
    phi=0.2,
    photonType=PhotonType('1'),
    line=FluorescentLine('13'),
    numOfScatterings=1,
    totalPathLength=1e12,
    numOfClouds=3,
    escapePosition=np.array([1e10, 1e10, 1e10]),
    effectiveLength=1e8,
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

    photonType: PhotonType

    line: FluorescentLine

    numOfScatterings: int
    """number of compton scatterings
    """
    totalPathLength: float
    """total path length that the photon
    traveled inside the torus before it was registered
    """

    numOfClouds: int
    """number of clouds on the photon's escape line
    """

    escapePosition: np.ndarray
    """position where the photon was registered
    """

    effectiveLength: float
    """the length inside the clouds intersected
    by the photon's escape line
    """

    def n_h_escape_line(self, hydrogen_concentration: float) -> float:
        """Get the Column Density on the photons escape line

        Args:
            hydrogen_concentration (float): Concentration of hydrogen in matter

        Returns:
            float: The column density of the photon's escape line
        """
        return hydrogen_concentration*self.effectiveLength

    @staticmethod
    def build_photon_raw_info(raw_info:str)-> PhotonRawInfo:
        hv_str, theta_str, phi_str, photon_type_str, line_str, numOfScatterings_str, totalPathLength_str, numOfClouds_str, x_str,y_str,z_str,effectiveLength_str = raw_info.split()
        return PhotonRawInfo(
            hv=float(hv_str),
            theta=float(theta_str),
            phi=float(phi_str),
            photonType=PhotonType(type_label=photon_type_str),
            line=FluorescentLine(line_label=line_str),
            numOfScatterings=int(numOfScatterings_str),
            totalPathLength=float(totalPathLength_str),
            numOfClouds=int(numOfClouds_str),
            escapePosition=np.array([float(x_str),float(y_str),float(z_str)]),
            effectiveLength=float(effectiveLength_str)
        )
