from __future__ import annotations
from measurements import parse_measurement, ValueAndError
from typing import Tuple, Dict, List
import numpy as np


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


def get_shoulder_vs_nhaver(measurements_filepath: str) -> Dict[str, List[ValueAndError]]:
    data: Dict[str, List[ValueAndError]] = {}

    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)

            if key.nh_aver not in data:
                data[key.nh_aver] = []

            data[key.nh_aver] += [value.shoulder]

    return data