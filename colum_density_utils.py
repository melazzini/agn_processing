"""
==================================

Example-01: 'how to build a column density list from a file with effective lengths'

effective_lengths = get_effective_lengths(
    path_to_effective_lengths_file="/path/to/effectiveLengths")

sim_info = AgnSimulationInfo.build_agn_simulation_info(
sim_root_dir="/path/to/sim_root_dir")

nh_list = build_nh_list_from_effective_lengths(
effective_lengths=effective_lengths, sim_info=sim_info)

print(nh_list)

==================================


==================================

Example: 'How to build and use a column density distribution'

# See Example-01 to build the nh_list

nh_distribution = ColumnDensityDistribution(grid=grid, nh_list=nh_list)

print(*[f'{nh_i:>8.3g}: {nh_distribution.get_distribution_value_for_nh(nh_i):>8.3g}'
      for nh_i in np.logspace(start=22, stop=24, num=30)], sep='\n')
      
      
==================================

"""


from utils import *
from agn_utils import AgnSimulationInfo
import pint
from agn_simulation_policy import AGN_SIMULATION_UNITS, AGN_PROCESSING_UNITS
from agn_processing_policy import LEFT_NH, NH_INTERVALS, RIGHT_NH


class ColumnDensityInterval(Interval2D):
    pass


class ColumnDensityGrid:
    """
    This class defines the grid of column densities
    used to group spectrum data from agn simulations.

    Basically, you use it to get the index of the given
    column density on the whole grid for the current project.

    This can be useful to group spectrum data and build labels
    for spectrum files, according to the given values of
    the column density.

    You are not require to use any specific units, but
    probably you want to work in [N_H]=cm^{-2}.

    ===========================

    example01:

    nh_grid = ColumnDensityGrid(left_nh=1e22, right_nh=2e24, n_intervals=30)

    print(nh_grid.index(nh=1e23))

    ==========================
    """

    def __init__(self, left_nh: float, right_nh: float, n_intervals: int):
        """Initializes the Grid

        Args:
            left_nh (float): the left-most bound of the grid
            right_nh (float): the right-most bound of the grid
            n_intervals (int): the number of intervals of the grid
        """

        self.left = left_nh
        self.right = right_nh
        self.n_intervals = n_intervals

        self.bounds = []
        """the bounds of the grid
        """

        self.nh_list = []
        """the mid-values of the bounds
        """

        nh_bounds_raw = np.logspace(
            np.log10(self.left), np.log10(self.right), n_intervals+1)

        self.__setup_grid(nh_bounds_raw)
        self.d_nh = (np.log10(self.right) -
                     np.log10(self.left))/self.n_intervals

    def __setup_grid(self, nh_bounds_raw):
        for i, nh_left_val in enumerate(nh_bounds_raw[:-1]):
            self.nh_list += [(nh_left_val+nh_bounds_raw[i+1])/2]
            self.bounds += [ColumnDensityInterval(
                left=nh_left_val, right=nh_bounds_raw[i+1])]

    def index(self, nh: float):
        """Get the grid index of the given column density.

        Args:
            nh (float): the column density
        """
        if(nh <= 0):
            return 0

        return int((np.log10(nh)-np.log10(self.left))/self.d_nh)

    def __str__(self):
        return f'{self.left:0.2g}:{self.right:0.2g}:{self.n_intervals}'


def get_hydrogen_concentration(aver_column_density: float,
                               filling_factor: float,
                               internal_torus_radius: float,
                               external_torus_radius: float) -> float:
    """Get the concentration of Hydrogen in the matter.

    Be consistent with your units!

    Args:
        column_density (float): Average column density
        filling_factor (float): filling factor in the torus
        internal_torus_radius (float): 
        external_torus_radius (float): 

    Returns:
        float: Concentration of hydrogen.

    example:

    print(get_hydrogen_concentration(column_density=1e23,
                                 filling_factor=0.03,
                                 internal_torus_radius=1e14,
                                 external_torus_radius=1e15))
    """
    return aver_column_density/(filling_factor*(external_torus_radius-internal_torus_radius))


def _get_multiplication_factor_to_translate_from_sim_to_processing_units(dimensionality: str) -> float:
    ureg = pint.UnitRegistry()
    return (1.0*ureg[AGN_SIMULATION_UNITS[dimensionality]]).to(ureg[AGN_PROCESSING_UNITS[dimensionality]]).magnitude


def get_effective_lengths(path_to_effective_lengths_file: str) -> np.ndarray:
    data = np.loadtxt(path_to_effective_lengths_file)
    return data*_get_multiplication_factor_to_translate_from_sim_to_processing_units(dimensionality=LENGTH)


def build_nh_list_from_effective_lengths(effective_lengths: np.ndarray, sim_info: AgnSimulationInfo) -> np.ndarray:
    hydrogen_concentration = get_hydrogen_concentration(aver_column_density=sim_info.nh_aver,
                                                        filling_factor=sim_info.phi,
                                                        internal_torus_radius=sim_info.r1,
                                                        external_torus_radius=sim_info.r2
                                                        )

    return effective_lengths*hydrogen_concentration


class ColumnDensityDistribution:

    def __init__(self, nh_grid: ColumnDensityGrid, nh_list: np.ndarray):
        self.grid = nh_grid
        self._histogram = Histo(bins=np.array(self.grid.nh_list), counts=np.zeros(
            self.grid.n_intervals), raw_data=nh_list)
        self._build_histogram(histogram=self._histogram)

    def _build_histogram(self, histogram: Histo):
        for nh_i in histogram.raw_data:
            index = self.grid.index(nh_i)
            histogram.counts[index] += 1

        histogram.counts /= sum(histogram.counts)

    def get_distribution_value_for_nh(self, nh: float) -> float:
        return self._histogram.counts[self.grid.index(nh=nh)]
