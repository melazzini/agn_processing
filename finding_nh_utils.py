from __future__ import annotations
from dataclasses import dataclass
from utils import AngularInterval, ValueAndError
from agn_simulation_policy import AGN_NH_AVERAGE, AGN_IRON_ABUNDANCE, AGN_VIEWING_DIRECTIONS_DEG
from colum_density_utils import ColumnDensityGrid
from agn_processing_policy import *
from typing import Tuple
import numpy as np


@dataclass
class MeasurementsKey:
    """For example: MeasurementsKey.build_key('523_5_1xfe_7590_27')
    """

    label: str
    nh_aver: float
    n_aver: int
    a_fe: float
    alpha: AngularInterval
    nh_index: int

    def __str__(self):
        return self.label

    def __hash__(self) -> int:
        return hash(f'{self}')

    @staticmethod
    def build_key(label: str):
        nh_aver_code, n_aver_code, a_fe_code, alpha_code, nh_index_code = label.split(
            sep='_')
        nh_aver = AGN_NH_AVERAGE[nh_aver_code]
        n_aver = int(n_aver_code)
        a_fe = AGN_IRON_ABUNDANCE[a_fe_code]
        alpha = AGN_VIEWING_DIRECTIONS_DEG[alpha_code]
        nh_index = int(nh_index_code)
        return MeasurementsKey(label=label,
                               nh_aver=nh_aver,
                               n_aver=n_aver,
                               a_fe=a_fe,
                               alpha=alpha,
                               nh_index=nh_index)


@dataclass
class MeasurementsValue:
    """
    For example:

        measurements_value = MeasurementsValue.build_value(
    value_str='148.40451467268772:9.5012966217946   10.81218885277748:0.12967704020506401    0.28384380437824447:0.03464267951399144    0.7066970916271619:0.2879696561324931:13.431194255571947:20')


    """

    ew: ValueAndError
    h: ValueAndError
    shoulder: ValueAndError
    edge: ValueAndError
    edge_chi2_value: float
    edge_chi2_dof: int

    def __str__(self):
        return f'ew: {self.ew.value} +-{self.ew.err}\n'\
            f'h: {self.h.value} +-{self.h.err}\n'\
            f'shoulder: {self.shoulder.value} +-{self.shoulder.err}\n'\
            f'edge: {self.edge.value} +-{self.edge.err}\n'\
            f'edge-chi2: {self.edge_chi2_value}\n'\
            f'edge-dof: {self.edge_chi2_dof}'

    @staticmethod
    def build_value(value_str: str):
        ew_code, h_code, shoulder_code, edge_code = value_str.split()
        ew_value_code, ew_err_code = ew_code.split(sep=":")
        h_value_code, h_err_code = h_code.split(sep=":")
        shoulder_value_code, shoulder_err_code = shoulder_code.split(sep=":")
        edge_value_code, edge_err_code, edge_chi2_code, edge_chi2_dof_code = edge_code.split(
            sep=":")

        ew = ValueAndError(value=float(ew_value_code), err=float(ew_err_code))
        h = ValueAndError(value=float(h_value_code), err=float(h_err_code))
        shoulder = ValueAndError(value=float(
            shoulder_value_code), err=float(shoulder_err_code))
        edge = ValueAndError(value=float(edge_value_code),
                             err=float(edge_err_code))
        edge_chi2_value = float(edge_chi2_code)
        edge_chi2_dof = int(edge_chi2_dof_code)

        return MeasurementsValue(ew=ew, h=h, shoulder=shoulder, edge=edge, edge_chi2_value=edge_chi2_value, edge_chi2_dof=edge_chi2_dof)


def parse_measurement(measurement_line: str) -> Tuple[MeasurementsKey, MeasurementsValue]:
    key_code, value_code = measurement_line.split(sep='#')
    key = MeasurementsKey.build_key(label=key_code)
    value = MeasurementsValue.build_value(value_str=value_code)

    return key, value


def get_edge_vs_h(measurements_filepath: str, nh_index: int) -> Tuple[np.ndarray]:
    """Returns the edge vs h data to be plotted.
    
    For example:
    
        g = ColumnDensityGrid(LEFT_NH, RIGHT_NH, NH_INTERVALS)

        h, h_err, edge, edge_err = get_edge_vs_h(
            measurements_filepath="/path/to/measurements/file", nh_index=g.index(5e23))


        print(h)
        print(h_err)
        print(1-edge)
        print(edge_err)
    

    Args:
        measurements_filepath (str): the path to the measurements file
        nh_index (int): index on the given-and-corresponding nh_grid

    Returns:
        Tuple[np.ndarray]: h, h_err, edge, edge_err
    """

    h = []
    h_err = []
    edge = []
    edge_err = []
    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)

            if key.nh_index == nh_index:
                h += [value.h.value]
                h_err += [value.h.err]
                edge += [value.edge.value]
                edge_err += [value.edge.err]

    return np.array(h), np.array(h_err), np.array(edge), np.array(edge_err)

