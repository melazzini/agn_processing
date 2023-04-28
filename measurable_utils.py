from __future__ import annotations
from measurements import parse_measurement, ValueAndError, Measurement
from typing import Tuple, Dict, List
import numpy as np
from agn_utils import AngularInterval


def get_edge_vs_h(measurements_filepath: str, nh_index: int, a_fe: str = None) -> Tuple[np.ndarray]:
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

            if a_fe != None:
                if key.nh_index == nh_index and key.a_fe == a_fe:

                    if value.edge.err/(1-value.edge.value) > 0.1:
                        continue

                    if 0.80865 <= 1-value.edge.value <= 0.8087:
                        print(key)

                    h += [value.h.value]
                    h_err += [value.h.err]
                    edge += [value.edge.value]
                    edge_err += [value.edge.err]
            else:
                if key.nh_index == nh_index:

                    h += [value.h.value]
                    h_err += [value.h.err]
                    edge += [value.edge.value]
                    edge_err += [value.edge.err]

    return np.array(h), np.array(h_err), np.array(edge), np.array(edge_err)


def get_edge_vs_h_by_nh_aver(measurements_filepath: str, nh_index: int, nh_aver: str = None) -> Tuple[np.ndarray]:
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

            if key.nh_aver != nh_aver:
                continue

            if value.edge.err/(1-value.edge.value) > 0.2:
                continue

            if key.nh_index == nh_index:

                h += [value.h.value]
                h_err += [value.h.err]
                edge += [value.edge.value]
                edge_err += [value.edge.err]

    return np.array(h), np.array(h_err), np.array(edge), np.array(edge_err)


def get_shoulder_vs_nhaver(measurements_filepath: str) -> Dict[Tuple[str, str, bool, int], List[ValueAndError]]:
    data: Dict[Tuple[str, str, bool, int], List[ValueAndError]] = {}

    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)

            is_alpha_75 = False

            if key.alpha == AngularInterval(75, 15):
                is_alpha_75 = True

            if (key.nh_aver, key.a_fe, is_alpha_75, key.n_aver) not in data:
                data[key.nh_aver, key.a_fe, is_alpha_75, key.n_aver] = []

            data[key.nh_aver, key.a_fe, is_alpha_75,
                 key.n_aver] += [value.shoulder]

    return data


def get_ew_vs_n_aver(measurements_filepath: str, nh_index: int, a_fe: str):

    data: Dict[int, List[ValueAndError]] = {}

    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)

            if key.nh_index != nh_index or key.a_fe != a_fe:
                continue

            if key.n_aver not in data:
                data[key.n_aver] = []

            data[key.n_aver] += [value.ew]
            print(f'the data: {data}')

    return data


def load_data_from_file(measurements_filepath: str) -> List[Measurement]:

    data: List[Measurement] = []

    with open(measurements_filepath) as measurements_file:
        for line in measurements_file:
            key, value = parse_measurement(measurement_line=line)
            data += [Measurement(key=key, value=value)]

    return data


def filter_data_by_nh(data: List[Measurement], nh_index: int):

    filtered_data: List[Measurement] = []

    for measurement in data:
        if measurement.key.nh_index == nh_index:
            filtered_data += [measurement]

    return filtered_data


def filter_data_by_nhaver(data: List[Measurement], nh_aver: str):

    filtered_data: List[Measurement] = []

    for measurement in data:
        if measurement.key.nh_aver == nh_aver:
            filtered_data += [measurement]

    return filtered_data


def filter_data_by_abundance(data: List[Measurement], a_fe: str):

    filtered_data: List[Measurement] = []

    for measurement in data:
        if measurement.key.a_fe == a_fe:
            filtered_data += [measurement]

    return filtered_data


def filter_data_by_viewing_angle(data: List[Measurement], alpha: AngularInterval):

    filtered_data: List[Measurement] = []

    for measurement in data:
        if measurement.key.alpha == alpha:
            filtered_data += [measurement]

    return filtered_data
