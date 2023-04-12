"""
This module should build the spectral_data/ directories,
from where we will extract the sum spectra and flux densities
obtained from the simulations processed spectra.
"""
from utils import AngularInterval
from paths_in_this_machine import repo_directory
from typing import Final, Dict, List
from agn_utils import *
import os
import numpy as np
from colum_density_utils import ColumnDensityGrid, ColumnDensityDistribution
from agn_processing_policy import *
from spectrum_utils import SpectrumCount, PoissonSpectrumCountFactory
from flux_density_utils import FluxDensityBuilder, FluxDensity


IRON_ABUNDANCES = {
    0.5: '05xfe',
    0.7: '07xfe',
    1: '1xfe',
    1.5: '15xfe',
    2: '2xfe',
}


def simulations_root_dir(nh_aver: float) -> str:
    """This function returns the root simulations directory for the given parameters.

    Args:
        nh_aver (float): average column density

    Returns:
        str: the path to the simulations root directory
    """

    if nh_aver == 1e23:
        return os.path.join(repo_directory, 'N_H_23')
    elif nh_aver == 2e23:
        return os.path.join(repo_directory, 'N_H_223')
    elif nh_aver == 5e23:
        return os.path.join(repo_directory, 'N_H_523')
    else:
        raise ValueError(
            f'The simulation directory for nh={nh_aver} cannot be determined!')


def get_spectra_directory_name(alpha: AngularInterval, grid: ColumnDensityGrid) -> str:

    for label in AGN_VIEWING_DIRECTIONS_DEG:
        if AGN_VIEWING_DIRECTIONS_DEG[label] == alpha:
            return f'THETA_{label}_nh_grid_{grid.n_intervals}_{grid.left:0.2g}_{grid.right:0.2g}'


def get_spectra_directories(simulations: List[AgnSimulationInfo], alpha: AngularInterval, grid: ColumnDensityGrid):

    spectra_dirs = []

    for simulation_i in simulations:
        sim_dir = simulation_i.sim_root_dir

        spectra_dir = os.path.join(sim_dir,
                                   get_spectra_directory_name(alpha=alpha, grid=grid))

        if os.path.exists(spectra_dir):
            spectra_dirs += [spectra_dir]

    return spectra_dirs


@dataclass
class SpectrumKind:
    grid_id: int
    type_label: str
    line_label: str

    def __hash__(self):
        return hash(self.__str__())

    def build(spectrum_label: str):
        g_str, t_str, l_str = spectrum_label.split(sep='_')
        return SpectrumKind(grid_id=int(g_str), type_label=t_str, line_label=l_str)

    def __str__(self) -> str:
        return f'{self.grid_id}_{self.type_label}_{self.line_label}'


def get_grouped_spectra_files(spectra_dirs: List[str]) -> Dict[SpectrumKind, List[str]]:

    spectra: Dict[SpectrumKind, List[str]] = {}

    for spectra_dir_i in spectra_dirs:
        for spectrum_file in os.listdir(spectra_dir_i):
            spectrum_kind = SpectrumKind.build(
                spectrum_label=spectrum_file.split(sep='.')[0])

            if spectrum_kind not in spectra:
                spectra[spectrum_kind] = []

            spectra[spectrum_kind] += [
                os.path.join(spectra_dir_i, spectrum_file)]

    return spectra


def build_continuum_spectra_map(grouped_spectra: Dict[SpectrumKind, SpectrumCount]) -> Dict[SpectrumKind, SpectrumCount]:

    data_map: Dict[SpectrumKind, SpectrumCount] = {}

    for spectrum_key in grouped_spectra:

        if spectrum_key.type_label in ('NOINTERACTION', 'SCATTERING'):

            continuum_spectrum_key = SpectrumKind(
                grid_id=None, type_label='CONTINUUM', line_label='NONE')

            continuum_spectrum_key.grid_id = spectrum_key.grid_id

            if continuum_spectrum_key not in data_map:
                data_map[continuum_spectrum_key] = grouped_spectra[spectrum_key]
            else:
                data_map[continuum_spectrum_key].y += grouped_spectra[spectrum_key].y
                data_map[continuum_spectrum_key].y_err = data_map[continuum_spectrum_key].y**0.5

    return data_map


def build_transmitted_spectra_map(grouped_spectra: Dict[SpectrumKind, SpectrumCount]) -> Dict[SpectrumKind, SpectrumCount]:

    data_map: Dict[SpectrumKind, SpectrumCount] = {}

    for spectrum_key in grouped_spectra:

        if spectrum_key.type_label in ('NOINTERACTION', 'SOURCE'):

            continuum_spectrum_key = SpectrumKind(
                grid_id=None, type_label='TRANSMITTED', line_label='NONE')

            continuum_spectrum_key.grid_id = spectrum_key.grid_id

            if continuum_spectrum_key not in data_map:
                data_map[continuum_spectrum_key] = grouped_spectra[spectrum_key]
            else:
                data_map[continuum_spectrum_key].y += grouped_spectra[spectrum_key].y
                data_map[continuum_spectrum_key].y_err = data_map[continuum_spectrum_key].y**0.5

    return data_map


def build_compton_spectra_map(grouped_spectra: Dict[SpectrumKind, SpectrumCount]) -> Dict[SpectrumKind, SpectrumCount]:

    data_map: Dict[SpectrumKind, SpectrumCount] = {}

    for spectrum_key in grouped_spectra:

        if spectrum_key.type_label in ('SCATTERING'):

            continuum_spectrum_key = SpectrumKind(
                grid_id=None, type_label='COMPTON', line_label='NONE')

            continuum_spectrum_key.grid_id = spectrum_key.grid_id

            if continuum_spectrum_key not in data_map:
                data_map[continuum_spectrum_key] = grouped_spectra[spectrum_key]
            else:
                data_map[continuum_spectrum_key].y += grouped_spectra[spectrum_key].y
                data_map[continuum_spectrum_key].y_err = data_map[continuum_spectrum_key].y**0.5

    return data_map


def build_fekalpha_spectra_map(grouped_spectra: Dict[SpectrumKind, SpectrumCount]) -> Dict[SpectrumKind, SpectrumCount]:

    data_map: Dict[SpectrumKind, SpectrumCount] = {}

    for spectrum_key in grouped_spectra:

        if spectrum_key.line_label == 'FeKalpha':

            continuum_spectrum_key = SpectrumKind(
                grid_id=spectrum_key.grid_id, type_label='FLUORESCENT', line_label='FeKalpha')

            if continuum_spectrum_key not in data_map:
                data_map[continuum_spectrum_key] = grouped_spectra[spectrum_key]
            else:
                data_map[continuum_spectrum_key].y += grouped_spectra[spectrum_key].y
                data_map[continuum_spectrum_key].y_err = data_map[continuum_spectrum_key].y**0.5

    return data_map


def build_key_spectrum_flux_density_map(grouped_spectra: Dict[SpectrumKind, SpectrumCount], nh_distribution: ColumnDensityDistribution, source_spectrum: SpectrumCount, alpha_deg: AngularInterval) -> Dict[SpectrumKind, Tuple[SpectrumCount, FluxDensity]]:

    data_map = {}

    for spectrum_key in grouped_spectra:

        nh = nh_distribution.grid.nh_list[spectrum_key.grid_id]
        spectrum = grouped_spectra[spectrum_key]
        try:
            flux_density = FluxDensityBuilder.build_flux_density_for_given_nh(spectrum_count=spectrum,
                                                                              norm_spectrum=source_spectrum,
                                                                              angle_interval=alpha_deg.from_deg_to_rad(),
                                                                              nh=nh,
                                                                              nh_distribution=nh_distribution)

            data_map[spectrum_key] = (spectrum, flux_density)
        except:
            continue

    return data_map


def get_nh_aver_label(sims_root_dir: str):
    return sims_root_dir.split(sep='/')[-1].split(sep='_')[2]


def group_spectra(grouped_spectra_files: Dict[SpectrumKind, List[str]]) -> Dict[SpectrumKind, SpectrumCount]:

    return {
        k: PoissonSpectrumCountFactory.build_spectrum_count(*grouped_spectra_files[k]) for k in grouped_spectra_files}
