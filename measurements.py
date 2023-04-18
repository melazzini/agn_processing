from os import listdir, path, mkdir, path
from agn_processing_policy import *
from paths_in_this_machine import root_simulations_directory
from functools import reduce
from dataclasses import dataclass
from flux_density_utils import FluxDensity, EnergyInterval, product_transport_err, ValueAndError, SpectrumCount, get_interval_index_log, HV_CONTINUUM_AT_FEKALPHA_LEFT, HV_CONTINUUM_AT_FEKALPHA_RIGHT, parse_spectral_data_files, HV_FEKALPHA_NO_SHOULDER_LEFT, HV_FEKALPHA_SHOULDER_RIGHT, HV_FEKALPHA_ABSORPTION_EDGE, HV_FEKALPHA_ABSORPTION_LEFT_LEFT, HV_FEKALPHA_ABSORPTION_RIGHT_LEFT, HV_FEKALPHA_ABSORPTION_RIGHT_RIGHT, AngularInterval
from agn_simulation_policy import AGN_NH_AVERAGE, AGN_IRON_ABUNDANCE, AGN_VIEWING_DIRECTIONS_DEG
import numpy as np
from typing import Dict, List, Tuple
from spectrum_utils import SpectrumBase
from utils import chi2
from agn_utils import compton_shift
from scipy.optimize import curve_fit
from inspect import signature

root_dir = root_simulations_directory
spectral_data_file_label = "spectral_data"


class AbsorptionEdgeFitter:
    """
    This is a functor class to fit the Iron Absorption Edge.
    """

    def __init__(self, hv_left_left: float,
                 hv_left_right: float,
                 hv_right_left: float,
                 hv_right_right: float,
                 max_number_trials: float = 1e6,
                 custom_fitter=None) -> None:
        """Create a fitter instance

        Args:
            hv_left_left (float): left energy bound of the left region
            hv_left_right (float): right energy bound of the left region
            hv_right_left (float): left energy bound of the right region
            hv_right_right (float): right energy bound of the right region
            max_number_trials (float, optional): maximum number of trial. Defaults to 1e6.
            custom_fitter (callable, optional): custom fitter. Defaults to None.
        """

        self.hv_left_left = hv_left_left
        self.hv_left_right = hv_left_right
        self.hv_right_left = hv_right_left
        self.hv_right_right = hv_right_right
        self.max_number_trials = max_number_trials
        self.fitter = custom_fitter if custom_fitter else self._get_fitter()
        sig = signature(self.fitter)
        self.num_params_of_fitter = len(sig.parameters)

    def __call__(self, spectrum: SpectrumCount) -> Tuple[SpectrumCount, SpectrumCount, float, float, float]:
        """fit the given spectrum

        Args:
            spectrum (SpectrumCount): the continuum spectrum near the absorption edge

        Returns:
            Tuple[SpectrumCount, SpectrumCount, float, float, float]: part of the continuum that was fitted, \
                the fitted continuum, edge, edge error, xi2
        """

        formated_spectrum = self._format_spectrum_to_be_fitted(spectrum)

        fitter = self._get_fitter()
        pars, cov = curve_fit(f=fitter, xdata=formated_spectrum.x,
                              ydata=formated_spectrum.y,
                              bounds=([-np.inf for i in range(self.num_params_of_fitter-2)] + [0],
                                      [np.inf for i in range(self.num_params_of_fitter-2)]+[1]),
                              sigma=formated_spectrum.y_err,
                              absolute_sigma=True,
                              maxfev=self.max_number_trials)

        # x = formated_spectrum.x
        # y = fitter(x, *pars)

        # # print(len(np.absolute(formated_spectrum.y-y)))
        # # print(len(formated_spectrum.y_err))
        # # print(np.absolute(formated_spectrum.y-y))
        # # print(formated_spectrum.y_err)

        # true_err = [a if a > b else b for a, b in zip(
        #     np.absolute(formated_spectrum.y-y), formated_spectrum.y_err)]

        # pars, cov = curve_fit(f=fitter, xdata=formated_spectrum.x,
        #                       ydata=formated_spectrum.y,
        #                       bounds=([-np.inf for i in range(self.num_params_of_fitter-2)] + [0],
        #                               [np.inf for i in range(self.num_params_of_fitter-2)]+[1]),
        #                       sigma=np.array(true_err),
        #                       absolute_sigma=True, maxfev=self.max_number_trials)

        x = formated_spectrum.x
        y = fitter(x, *pars)
        y_err = np.sqrt(y)
        expected_spectrum = SpectrumCount(x, y, y_err)

        xi2_val, dof = self._chi2_N_fe_fit(
            observed=formated_spectrum, expected=expected_spectrum)

        *_, N_edge = pars
        perr = np.sqrt(np.diag(cov))
        *_, N_edge_err = perr

        # print(pars)
        # print(perr)
        # plt.plot(formated_spectrum.x, formated_spectrum.y)
        # plt.plot(expected_spectrum.x, expected_spectrum.y)

        return formated_spectrum, expected_spectrum, N_edge, N_edge_err, xi2_val, dof

    def _get_fitter(self):

        def fitter(energy_intervals: np.ndarray, m, b, N_fit):
            zero_spectrum = SpectrumCount(
                energy_intervals, 0*energy_intervals, 0*energy_intervals)

            left_spectrum = zero_spectrum.get_cpy_on_interval(
                EnergyInterval(self.hv_left_left, self.hv_left_right))
            right_spectrum = zero_spectrum.get_cpy_on_interval(
                EnergyInterval(self.hv_right_left, self.hv_right_right))
            center_zero_spectrum = zero_spectrum.get_cpy_on_interval(
                EnergyInterval(self.hv_left_right, self.hv_right_left))

            left_count = (m*left_spectrum.x) + b
            right_count = N_fit * ((m*right_spectrum.x) + b)

            return np.concatenate((left_count, center_zero_spectrum.y, right_count))        

        return fitter

    def _format_spectrum_to_be_fitted(self, spectrum: SpectrumBase):
        left_spectrum = spectrum.get_cpy_on_interval(
            EnergyInterval(self.hv_left_left, self.hv_left_right))
        right_spectrum = spectrum.get_cpy_on_interval(
            EnergyInterval(self.hv_right_left, self.hv_right_right))
        center_spectrum = spectrum.get_cpy_on_interval(
            EnergyInterval(self.hv_left_right, self.hv_right_left))

        center_spectrum.y *= 0

        spectrum_x = np.concatenate(
            (left_spectrum.x, center_spectrum.x, right_spectrum.x))
        spectrum_y = np.concatenate(
            (left_spectrum.y, center_spectrum.y, right_spectrum.y))
        spectrum_y_err = np.concatenate(
            (left_spectrum.y_err, center_spectrum.y_err, right_spectrum.y_err))

        return SpectrumBase(spectrum_x, spectrum_y, spectrum_y_err)

    def _chi2_N_fe_fit(self, observed: SpectrumBase, expected: SpectrumBase):
        left_observed = observed.get_cpy_on_interval(
            EnergyInterval(self.hv_left_left, self.hv_left_right))
        right_observed = observed.get_cpy_on_interval(
            EnergyInterval(self.hv_right_left, self.hv_right_right))

        left_expected = expected.get_cpy_on_interval(
            EnergyInterval(self.hv_left_left, self.hv_left_right))
        right_expected = expected.get_cpy_on_interval(
            EnergyInterval(self.hv_right_left, self.hv_right_right))

        full_observed = np.concatenate((left_observed.y, right_observed.y))
        full_expected = np.concatenate((left_expected.y, right_expected.y))

        # we subtract 1 because the first param is the energy intervals
        # array, and we don't have to consider it to calculate the
        # degrees of freedom
        dof = len(full_observed)-(self.num_params_of_fitter-1)

        return chi2(observed=full_observed, expected=full_expected), dof


def get_hardness(continuum_fd: FluxDensity,
                 hv_interval_left: EnergyInterval = EnergyInterval(
                     HV_HARDNESS_LEFT_LEFT, HV_HARDNESS_LEFT_RIGHT),
                 hv_interval_right: EnergyInterval = EnergyInterval(HV_HARDNESS_RIGHT_LEFT, HV_HARDNESS_RIGHT_RIGHT)):
    continuum_flux_left = continuum_fd.get_cpy_on_interval(
        hv_interval_left).flux()
    continuum_flux_right = continuum_fd.get_cpy_on_interval(
        hv_interval_right).flux()
    h = continuum_flux_right.value/continuum_flux_left.value
    h_err = h * \
        product_transport_err([continuum_flux_left, continuum_flux_right])

    return ValueAndError(h, h_err)


def get_ew(fekalpha_fd: FluxDensity, continuum_fd: FluxDensity):
    fekalpha_flux = fekalpha_fd.flux()

    continuum_at_fekalpha = continuum_fd.average(EnergyInterval(
        HV_CONTINUUM_AT_FEKALPHA_LEFT, HV_CONTINUUM_AT_FEKALPHA_RIGHT))

    ew = fekalpha_flux.value / continuum_at_fekalpha.value
    ew_err = ew*product_transport_err([fekalpha_flux, continuum_at_fekalpha])

    return ValueAndError(ew, ew_err)


def get_fekalpha_compton_shoulder(fekalpha_fd: FluxDensity) -> ValueAndError:
    fekalpha_line_shoulder = fekalpha_fd.get_cpy_on_interval(
        EnergyInterval(left=HV_LEFT, right=HV_FEKALPHA_SHOULDER_RIGHT))

    shoulder_flux = fekalpha_line_shoulder.flux()
    line_flux = fekalpha_fd.flux()
    d_compton = shoulder_flux.value/line_flux.value
    d_compton_err = d_compton * \
        product_transport_err([shoulder_flux, line_flux])

    return ValueAndError(d_compton, d_compton_err)


def get_edge(continuum_sp: SpectrumCount, fitter: AbsorptionEdgeFitter):
    _, _, edge, edge_err, chi2, dof = fitter(spectrum=continuum_sp)
    return ValueAndError(edge, edge_err), chi2, dof


@dataclass
class GridMetaData:
    n_intervals: int

    left: str
    """for example: 8.9e+21
    """

    right: str
    """for example:8.9e+25
    """

    def __str__(self):
        return f'{self.n_intervals}_{self.left}_{self.right}'

    def build(code: str):
        n_intervals_str, left, right = code.split(sep='_')

        return GridMetaData(n_intervals=int(n_intervals_str), left=left, right=right)


@dataclass
class SpectralDataFileInfo:
    nh_aver: str
    """for example: 223/24/etc
    """

    n_aver: int

    a_fe: str
    """for example: 1xfe,
    """

    alpha: str
    """for example: 6075/7590
    """

    grid_metadata: GridMetaData
    """for example: 40_8.9e+21_8.9e+25_1 
    """
    grid_id: int

    type_label: str
    """for example: CONTINUUM/FLUORESCENT/etc
    """

    line_label: str
    """for example: FeKalpha/etc
    """

    file_data_type: str
    """for example: spectrum/fluxdensity
    """

    path_to_file: str

    def __str__(self):
        return f'{self.nh_aver}_{self.n_aver}_{self.a_fe}_{self.alpha}_{self.grid_id}'
        # return f'{self.nh_aver}_{self.n_aver}_{self.a_fe}_{self.alpha}_{self.grid_id}_{self.grid_metadata}_{self.type_label}.{self.file_data_type}'

    def build_spectral_data_info(path_to_file: str):

        filename = path_to_file.split(sep='/')[-1]

        file_data_type = ""

        if 'fluxdensity' in filename:
            spectral_data = filename.removesuffix('.fluxdensity')
            file_data_type = 'fluxdensity'
        elif 'spectrum' in filename:
            spectral_data = filename.removesuffix('.spectrum')
            file_data_type = 'spectrum'
        else:
            raise ValueError(
                f"the file {path_to_file} seems to have a wrong formatted name!")

        nh, na, a_fe, alpha, grid_n, grid_left, grid_right, grid_id, type_label, line_label = spectral_data.split(
            '_')

        return SpectralDataFileInfo(nh_aver=nh,
                                    n_aver=na,
                                    a_fe=a_fe,
                                    alpha=alpha,
                                    grid_metadata=GridMetaData(n_intervals=int(
                                        grid_n), left=grid_left, right=grid_right),
                                    grid_id=int(grid_id),
                                    type_label=type_label,
                                    line_label=line_label,
                                    file_data_type=file_data_type,
                                    path_to_file=path_to_file)


def get_wanted_spectral_data(considered_nh_indexes: List[int], *root_dirs: str) -> Tuple[Dict[str, FluxDensity], Dict[str, SpectrumCount], Dict[str, FluxDensity]]:
    """Returns the continuum flux density, continuum spectrum and fekalpha fluxdensity maps according to the considered nh indexes.

    Args:
        considered_nh_indexes (List[int]): the considered indexes to get the data

    Returns:
        Tuple[Dict[str, SpectralDataFileInfo], Dict[str, SpectralDataFileInfo], Dict[str, SpectralDataFileInfo]]: continuum_fd_map,continuum_sp_map,fekalpha_fd_map
    """

    continuum_fd_map: Dict[str, FluxDensity] = {}
    continuum_sp_map: Dict[str, SpectrumCount] = {}
    fekalpha_fd_map: Dict[str, FluxDensity] = {}

    for root_dir in root_dirs:
        print('=====================================')
        spectral_data_dir = path.join(root_dir, spectral_data_file_label)
        if spectral_data_file_label in listdir(root_dir) and path.isdir(spectral_data_dir):

            for spectral_data_file_name in listdir(spectral_data_dir):
                spectral_data_filepath = path.join(
                    spectral_data_dir, spectral_data_file_name)
                spectral_info = SpectralDataFileInfo.build_spectral_data_info(
                    path_to_file=spectral_data_filepath)

                if spectral_info.grid_id in considered_nh_indexes:

                    if spectral_info.type_label == 'CONTINUUM' and spectral_info.file_data_type == 'fluxdensity':

                        continuum_fd_map[f'{spectral_info}'] = FluxDensity(
                            *parse_spectral_data_files(spectral_info.path_to_file))

                    if spectral_info.type_label == 'CONTINUUM' and spectral_info.file_data_type == 'spectrum':

                        continuum_sp_map[f'{spectral_info}'] = SpectrumCount(
                            *parse_spectral_data_files(spectral_info.path_to_file))

                    if spectral_info.type_label == 'FLUORESCENT' and spectral_info.file_data_type == 'fluxdensity' and spectral_info.line_label == 'FeKalpha':

                        fekalpha_fd_map[f'{spectral_info}'] = FluxDensity(
                            *parse_spectral_data_files(spectral_info.path_to_file))

    return continuum_fd_map, continuum_sp_map, fekalpha_fd_map


def perform_measurements(considered_nh_indexes: List[int], output_filepath: str, *root_dirs):
    """This function takes the spectrum and flux densities in spectral_data directories and
    measures ew, h, shoulder, edge, with their corresponding errors. The data will be stored
    in the given file.

    Args:
        considered_nh_indexes (List[int]): Indexes from the NH grid
        output_filepath (str): where to store the measurements
    """

    continuum_fd_map, continuum_sp_map, fekalpha_fd_map = get_wanted_spectral_data(considered_nh_indexes,
                                                                                   *root_dirs)

    fitter = AbsorptionEdgeFitter(
        hv_left_left=HV_FEKALPHA_ABSORPTION_LEFT_LEFT,
        hv_left_right=compton_shift(HV_FEKALPHA_ABSORPTION_EDGE),
        hv_right_left=HV_FEKALPHA_ABSORPTION_RIGHT_LEFT,
        hv_right_right=HV_FEKALPHA_ABSORPTION_RIGHT_RIGHT)

    with open(output_filepath, 'w') as measurements_file:
        for fekalpha_line_key in fekalpha_fd_map:

            fekalpha_fd = fekalpha_fd_map[fekalpha_line_key]
            continuum_fd = continuum_fd_map[fekalpha_line_key]
            continuum_sp = continuum_sp_map[fekalpha_line_key]

            ew = get_ew(fekalpha_fd=fekalpha_fd, continuum_fd=continuum_fd)
            h = get_hardness(continuum_fd=continuum_fd)
            compton_shoulder = get_fekalpha_compton_shoulder(
                fekalpha_fd=fekalpha_fd)
            try:
                edge, chi2_, dof = get_edge(
                    continuum_sp=continuum_sp, fitter=fitter)
            except ValueError as e:
                print(
                    f'error while fitting the absorption edge({fekalpha_line_key}): {e}')
                continue

            measurements_file.write(
                f'{fekalpha_line_key}#{ew.value}:{ew.err}   {h.value}:{h.err}    {compton_shoulder.value}:{compton_shoulder.err}    {edge.value}:{edge.err}:{chi2_}:{dof}\n')


@dataclass
class MeasurementsKey:
    """For example: MeasurementsKey.build_key('523_5_1xfe_7590_27')
    """

    label: str
    nh_aver: str
    n_aver: int
    a_fe: str
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
        nh_aver = nh_aver_code
        n_aver = int(n_aver_code)
        a_fe = a_fe_code
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
