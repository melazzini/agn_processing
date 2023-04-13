from os import listdir, path, mkdir, path
from agn_utils import AgnSimulationInfo, AGN_EFFECTIVE_LENGTHS_DIR_LABEL, AGN_VIEWING_DIRECTIONS_DEG, get_effective_lengths_directions_filename
import subprocess
from paths_in_this_machine import root_simulations_directory, create_nh_distribution
from functools import reduce
from dataclasses import dataclass

TOTAL_DIRECTIONS = 1_000_000

root_dir = root_simulations_directory
spectral_data_file_label = "spectral_data"


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
                                    grid_id=grid_id,
                                    type_label=type_label,
                                    line_label=line_label,
                                    file_data_type=file_data_type,
                                    path_to_file=path_to_file)


for root_dir in ["/home/francisco/Projects/agn/agn/AGNClumpySpecialization/build/results/N_H_223"]:
    print('=====================================')
    spectral_data_dir = path.join(root_dir, spectral_data_file_label)
    if spectral_data_file_label in listdir(root_dir) and path.isdir(spectral_data_dir):
        for spectral_data_file_name in listdir(spectral_data_dir):
            spectral_data_filepath = path.join(
                spectral_data_dir, spectral_data_file_name)
            spectral_info = SpectralDataFileInfo.build_spectral_data_info(
                path_to_file=spectral_data_filepath)

            print(spectral_info.file_data_type)
