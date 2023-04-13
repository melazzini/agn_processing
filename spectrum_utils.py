from __future__ import annotations
from typing import Final, List, Dict, Iterable, Set
from utils import *
from agn_utils import AgnSimulationInfo, AGN_SOURCE_DATA_STORAGE_PREFIX
from colum_density_utils import ColumnDensityGrid, get_hydrogen_concentration
from agn_processing_policy import *
from photon_register_policy import PhotonInfo, PhotonType, AgnPhotonUnitsPolicy
from io import TextIOWrapper
import os
import subprocess
from paths_in_this_machine import PATH_TO_CREATE_SOURCE_SPECTRA_DIR, ERRORS_LOG_FILE

"""TODO"""
SPECTRUM_PHOTON_TYPES_LABELS: Final[Dict[str, float]] = {
    # THE PHOTON COMES FROM THE SOURCE AND DID NOT INTERSECT ANY CLOUD OR MATTER IN THE TORUS
    'SOURCE': ('TRANSMITTED'),
    # THE PHOTON INTERSECTED THE TORUS CLOUDS/MATTER BUT IT DID NOT INTERACTED
    'NOINTERACTION': ('TRANSMITTED'),
    # THE PHOTON INTERACTED WITH THE TORUS BY COMPTON SCATTING
    'SCATTERING': ('COMPTON'),
    'FLUORESCENT': ('FLUORESCENT'),  # THIS IS A FLUORESCENT PHOTON
}


@dataclass
class SpectrumBaseItem:
    x: float
    y: float
    y_err: float


def get_interval_index_log(value: float, value_interval: Interval2D, num_of_intervals: int) -> int:
    """Returns the interval index corresponding to the given value. 
    The whole value interval is in a log10 scale

    Args:
        value (float): energy withing the interval
        value_interval (Interval2D): Full value interval
        num_of_intervals (int): number of bins

    Returns:
        int: the value interval index
    """
    return int(num_of_intervals * (np.log10(value/value_interval.left))/(np.log10(value_interval.right/value_interval.left)))


class SpectrumBase:
    """Represents a spectrum with:

        x: the x coordinate values, for example energy

        y: the spectrum values, for example flux-density

        y_err: the error on y values, for example the standard deviation

        Both x,y,y_err are grouped into @SpectrumBaseItem objects

    The user has to determine the meaning and units of x and y.

    The spectrum is also iterable.
    """

    def __init__(self, x: Iterable[float],
                 y: Iterable[float],
                 y_err: Iterable[float], interval: Interval2D = None):
        """Creates an instance of the class.

        Args:
            x (Iterable[float]): the x coordinate values, for example energy
            y (Iterable[float]): the spectrum values, for example flux-density
            y_err (Iterable[float]): the error on y values, for example the standard deviation
        """
        if len(x) == len(y) == len(y_err):
            self.length = len(x)
            self.pos = 0
            self.interval = None
            self.x = x
            self.y = y
            self.y_err = y_err

            if interval:
                self.interval = interval
            else:
                self.interval = Interval2D(x[0], x[-1])

            self.spectrum_list = np.empty(len(x), dtype=SpectrumBaseItem)
            for i in range(len(x)):
                self.spectrum_list[i] = SpectrumBaseItem(x[i], y[i], y_err[i])

        else:
            raise ValueAndError('The length of x,y, and y_err must be equal!')

    def __next__(self):
        pos = self.pos
        if pos < self.length:
            self.pos += 1
            return self.spectrum_list[pos]
        else:
            self.pos = 0
            raise StopIteration

    def __iter__(self):
        return self

    def __getitem__(self, index: int) -> SpectrumBaseItem:

        return self.spectrum_list[index]

    def __len__(self) -> int:
        return len(self.spectrum_list)

    # def components(self) -> Tuple[Iterable[float], Iterable[float], Iterable[float]]:
    #     """Returns a tuple with the copy of
    #     the x, y and y_err components
    #     of the spectrum

    #     Returns:
    #         Tuple[Iterable[float], Iterable[float], Iterable[float]]: x,y,y_err
    #     """
    #     return self.x, self.y, self.y_err

    # def algebraic_area(self):
    #     return np.trapz(x=self.x, y=self.y)

    # def algebraic_area_err(self):
    #     return np.sqrt(np.trapz(x=self.x, y=self.y_err**2))

    # def get_cpy_on_interval(self, energy_interval: EnergyInterval):
    #     """Returns the portion of the spectrum on the given interval

    #     Args:
    #         left (float): left value of the interval
    #         right (float): right value of the interval

    #     Returns:
    #         SpectrumBase: portion of the spectrum on [left, right]
    #     """
    #     cpy = self._get_cpy_on_interval(
    #         energy_interval.left, energy_interval.right, None)

    #     return type(self)(x=cpy.x, y=cpy.y, y_err=cpy.y_err)

    # def _get_cpy_on_interval(self, left: float, right: float = None, hole: bool = None):
    #     """
    #     This function returns the spectrum on the given interval.

    #     If the right parameter is not passed and hole=True, then the right
    #     energy bound will be so that the height at that point
    #     is not greater than the height at the first point, else
    #     the resulting spectrum will contain all the right points
    #     starting at the left point.
    #     """

    #     x, y, y_err = self.x, self.y, self.y_err

    #     new_x = []
    #     new_y = []
    #     new_y_err = []
    #     zipped = zip(x, y, y_err)
    #     if right != None:
    #         for x_i, y_i, y_err in zipped:
    #             if(left <= x_i <= right):
    #                 new_x += [x_i]
    #                 new_y += [y_i]
    #                 new_y_err += [y_err]
    #     elif hole:
    #         max_height = 0
    #         for x_i, y_i, y_err in zipped:
    #             if left <= x_i:
    #                 if(max_height > 0 and y_i >= max_height):
    #                     break
    #                 new_x += [x_i]
    #                 new_y += [y_i]
    #                 new_y_err += [y_err]
    #                 if(max_height <= 0):
    #                     max_height = new_y[0]

    #     elif hole == False:
    #         max_height = 0
    #         for x_i, y_i, y_err in zipped:
    #             if left <= x_i:
    #                 if(max_height > 0 and y_i <= max_height):
    #                     break
    #                 new_x += [x_i]
    #                 new_y += [y_i]
    #                 new_y_err += [y_err]

    #                 if(max_height <= 0):
    #                     max_height = new_y[0]

    #     return SpectrumBase(np.array(new_x), np.array(new_y), np.array(new_y_err))

    # def average_y(self, energy_interval: EnergyInterval) -> float:
    #     subspectrum = self.get_cpy_on_interval(energy_interval)
    #     return np.sum(subspectrum.y)/len(subspectrum.y)

    # def average(self, energy_interval: EnergyInterval = None) -> Tuple[ValueAndError, float]:

    #     if energy_interval == None:
    #         energy_interval = EnergyInterval(self.x[0], self.x[-1])

    #     subspectrum = self.get_cpy_on_interval(energy_interval)

    #     aver_x = np.sum(subspectrum.x)/len(subspectrum.x)
    #     index = get_interval_index_log(aver_x, Interval2D(
    #         energy_interval.left, energy_interval.right), len(subspectrum.x))
    #     aver_y = np.sum(subspectrum.y)/len(subspectrum.y)
    #     aver_y_err = np.sqrt(np.sum(subspectrum.y_err**2)) / \
    #         len(subspectrum.y_err)

    #     return ValueAndError(value=aver_y, err=aver_y_err), subspectrum.x[index]

    # def std_y(self, energy_interval: EnergyInterval) -> float:
    #     return np.std(self.get_cpy_on_interval(energy_interval).y)

    # def x_interval(self):
    #     return self.x[0], self.x[-1]


class SpectrumCount(SpectrumBase):
    """This class represents a the distribution-count
    of particles on the given x-coordinates. The x-coordinates
    can be for example energy bins. The y coordinate represents
    the number of particles on the given x.
    """

    def __init__(self, x: Iterable[float],
                 y: Iterable[float],
                 y_err: Iterable[float], interval: Interval2D = None):
        """Creates an instance of the spectrum counts

        Args:
            x (Iterable[float]): spectrum x coordinates
            y (Iterable[float]): spectrum values
            y_err (Iterable[float]): errors on the spectrum values
        """

        super().__init__(x, y, y_err, interval)


class PoissonSpectrumCountFactory:
    """This is a helper class to construct
    particle-distribution spectra with 
    Poisson distribution.

    Notice, that in this case the errors
    will be the square root of the number of
    particles.
    """

    @staticmethod
    def build_spectrum_count(*files: Iterable[str]) -> SpectrumCount:
        """This factory method returns the particle distribution
        corresponding to the given files.

        Args:
            files (Tupe[str]): paths to spectrum files
        Returns:
            SpectrumCount: The resulting Poisson spectrum count.
        """
        x, y = x_y(files[0])

        for i in range(1, len(files)):
            _, y_ = x_y(files[i])
            y = y+y_

        y_error = np.sqrt(y)

        return SpectrumCount(x, y, y_error)

    @staticmethod
    def build_log_empty_spectrum_count(hv_left: float, hv_right: float, n_intervals: int) -> SpectrumCount:

        d_nh_expo = (np.log10(hv_right)-np.log10(hv_left))/n_intervals
        hv_list = []

        for i in range(n_intervals):
            hv_ip1 = hv_left*10**(d_nh_expo*(i+1))
            hv_i = hv_left*10**(d_nh_expo*i)
            d_hv = hv_ip1 - hv_i
            hv_list += [hv_i + (d_hv/2)]

        x = np.array(hv_list)
        y = np.zeros(len(x))
        y_err = np.zeros(len(x))

        return SpectrumCount(x, y, y_err, EnergyInterval(hv_left, hv_right))


def _validate_index(index: int, hv: float, log_info: any = None) -> int:
    """There might be rare cases when the energy of the photon is out of the bounds.
    When this happens we can get exceptions in python when using the corresponding
    wrong indexes, thus we need to check the index values before using them.

    However, those cases are very rare and near the bounds so, we simply
    count those photons near the limits on the energy interval.

    This is an optional step and we can handle it in different ways according to the needs.

    Args:
        index (int): Apparent Index of the photon, which we seek to validate
        hv (float): Energy of the photon, for login info
        log_info (any, optional): Extra log info. Defaults to None.

    Returns:
        int: The validated index.
    """
    if index >= 2000:

        if os.path.getsize(ERRORS_LOG_FILE) > 1E9:
            os.remove(ERRORS_LOG_FILE)

        with open(ERRORS_LOG_FILE, '+a') as f:

            if log_info:
                f.write(f'{log_info}\n')

            f.write(f'The energy of the photon is: {hv}\n')
            f.write(f'The energy-index of the photon is: {index}\n')
            f.write(
                f'We count this rare case as being in the last bin of the energy grid.\n')
            f.write(
                '========================================================================\n')

        index = 1999

    if index < 0:
        if os.path.getsize(ERRORS_LOG_FILE) > 1E9:
            os.remove(ERRORS_LOG_FILE)

        with open(ERRORS_LOG_FILE, '+a') as f:
            if log_info:
                f.write(f'{log_info}\n')
            f.write(f'The energy of the photon is: {hv}\n')
            f.write(f'The energy-index of the photon is: {index}\n')
            f.write(
                f'We count this rare case as being in the first bin of the energy grid.\n')
            f.write(
                '========================================================================\n')

        index = 0

    return index


def count_photon_into_log_spectrum(spectrum: SpectrumCount, hv: float, optional_log_info: any = None):

    index = _validate_index(index=get_interval_index_log(
        hv, spectrum.interval, len(spectrum)), hv=hv, log_info=optional_log_info)

    spectrum[index].y += 1
    spectrum[index].y_err = spectrum[index].y**0.5
    return index


class PhotonRegistrationPolicy(ABC):

    @abstractmethod
    def get_label_for_photon(self, photon_info: PhotonInfo) -> str:
        pass


class NHPhotonRegistrationPolicy(PhotonRegistrationPolicy):

    def __init__(self, simulation_info: AgnSimulationInfo, nh_grid=ColumnDensityGrid(LEFT_NH, RIGHT_NH, NH_INTERVALS)) -> None:
        super().__init__()
        self.sim_info = simulation_info
        self.hydrogen_concentration = get_hydrogen_concentration(aver_column_density=self.sim_info.nh_aver,
                                                                 filling_factor=self.sim_info.phi,
                                                                 internal_torus_radius=self.sim_info.r1,
                                                                 external_torus_radius=self.sim_info.r2)
        self.grid = nh_grid

    def get_label_for_photon(self, photon_info: PhotonInfo) -> str:

        nh_grid_index = self.grid.index(
            photon_info.effective_column_density(self.hydrogen_concentration))

        return f'{nh_grid_index}_{photon_info.photon_type}_{photon_info.line}'


class SpectraBuilder:
    """This class builds the agn spectra files from a given simulation.
    It groups the spectra by the provided policy.
    """

    def __init__(self, sim_info: AgnSimulationInfo,
                 photon_registration_policy: PhotonRegistrationPolicy,
                 hv_interval: EnergyInterval = EnergyInterval(
                     HV_LEFT, HV_RIGHT),
                 hv_n_intervals: int = HV_N_INTERVALS,
                 photon_units_policy: UnitsPolicy = AgnPhotonUnitsPolicy(),
                 ) -> None:

        self.sim_info = sim_info

        self.photon_units_policy = photon_units_policy
        self.hv_interval = hv_interval
        self.hv_n_intervals = hv_n_intervals
        self.registration_policy = photon_registration_policy

    def build(self,
              angular_interval: AngularInterval,
              log_every_n_photons: int = 1000):

        spectra: Dict[str, SpectrumCount] = {}

        self.__process_simulation(
            sim_info=self.sim_info,
            spectra=spectra,
            angular_interval=angular_interval,
            log_every_n_photons=log_every_n_photons)

        return spectra

    def __log_status(self, file_label: str, n_photons_processed: int, limit: int = 1000):
        if not limit:
            return
        if n_photons_processed % limit == 0:
            print(
                f'Number of photons processed for {file_label}: {n_photons_processed}')

    def __register_photon(self, photon_info: PhotonInfo, spectra: Dict[str, SpectrumCount], error_log_info: any = None):

        spectrum_label = self.registration_policy.get_label_for_photon(
            photon_info=photon_info)

        if spectrum_label not in spectra:
            self.__generate_spectrum(spectra, spectrum_label)

        count_photon_into_log_spectrum(
            spectrum=spectra[spectrum_label],
            hv=photon_info.hv, optional_log_info=error_log_info)

    def __process_file(self,
                       file: TextIOWrapper, file_label: str,
                       angular_interval: AngularInterval,
                       log_every_n_photons: int,
                       spectra: Dict[str, SpectrumCount]):

        for photon_counter, line in enumerate(file):

            photon_info = PhotonInfo.build_photon_info(
                raw_info=line, policy=self.photon_units_policy)

            if photon_info.phi in angular_interval:
                self.__register_photon(
                    photon_info, spectra=spectra, error_log_info=f'{file_label}, #{photon_counter}')

            self.__log_status(
                file_label=file_label,
                n_photons_processed=photon_counter,
                limit=log_every_n_photons)

    def __process_simulation(self, sim_info: AgnSimulationInfo,
                             spectra: Dict[str, SpectrumCount],
                             angular_interval: AngularInterval,
                             log_every_n_photons: int):

        for file_path_i in sim_info.simulation_files:
            with open(file_path_i) as file_i:
                self.__process_file(file=file_i,
                                    file_label=file_path_i,
                                    angular_interval=angular_interval,
                                    log_every_n_photons=log_every_n_photons,
                                    spectra=spectra)

    def __generate_spectrum(self, spectra: Dict[str, SpectrumCount], label: str):
        spectra[label] = PoissonSpectrumCountFactory.build_log_empty_spectrum_count(
            hv_left=self.hv_interval.left,
            hv_right=self.hv_interval.right,
            n_intervals=self.hv_n_intervals
        )


def print_spectra(output_dir: str, spectra: Dict[str, SpectrumCount]):

    print('printing ...')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for spectrum_key in spectra:
        path_to_spectrum_file = os.path.join(
            output_dir, f'{spectrum_key}')

        with open(path_to_spectrum_file, mode='w') as file:

            for spectrum in spectra[spectrum_key]:
                file.write(
                    f'{spectrum.x:0.1f} {spectrum.y:0.1f} {spectrum.y_err}\n')

    print('done!')


class SourceSpectrumCountFileGenerator:

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def generate(self, num_of_photons: float, bins: int = 2000) -> str:

        new_source = f"source_S_{int(bins/1000)}k_{int(num_of_photons/1e6)}M.txt"

        path = os.path.join(self.root_dir, new_source)

        if not os.path.exists(path):
            if bins == 2000:
                subprocess.call([os.path.join(PATH_TO_CREATE_SOURCE_SPECTRA_DIR, 'create_source'),
                                str(num_of_photons), path])
            elif bins == 5000:
                subprocess.call([os.path.join(PATH_TO_CREATE_SOURCE_SPECTRA_DIR, 'create_source_5k'),
                                str(num_of_photons), path])
            elif bins == 10_000:
                subprocess.call([os.path.join(PATH_TO_CREATE_SOURCE_SPECTRA_DIR, 'create_source_10k'),
                                str(num_of_photons), path])
            elif bins == 30_000:
                subprocess.call([os.path.join(PATH_TO_CREATE_SOURCE_SPECTRA_DIR, 'create_source_30k'),
                                str(num_of_photons), path])
            else:
                ValueAndError

        return path


def generate_source_spectrum_count_file(num_of_photons: float, bins=2000) -> str:
    """
    =================================

    path_to_source_spectrum = generate_source_spectrum_count_file(
    num_of_photons=500_000000, bins=2000)

    print(f'path to source spectrum: {path_to_source_spectrum}')

    Args:
        num_of_photons (float): _description_
        bins (int, optional): _description_. Defaults to 2000.

    Returns:
        str: _description_
    """

    return SourceSpectrumCountFileGenerator(AGN_SOURCE_DATA_STORAGE_PREFIX).generate(num_of_photons, bins=bins)
