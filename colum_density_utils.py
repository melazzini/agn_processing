from utils import *


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

        for i, bounds in enumerate(self.bounds):
            if nh in bounds:
                return i
        else:
            None

    def __str__(self):
        return f'{self.left:0.2g}:{self.right:0.2g}:{self.n_intervals}'


def get_hydrogen_concentration(column_density: float,
                               filling_factor: float,
                               internal_torus_radius: float,
                               external_torus_radius: float) -> float:
    """Get the concentration of Hydrogen in the matter.

    Be consistent with your units!

    Args:
        column_density (float): Column density
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
    return column_density/(filling_factor*(external_torus_radius-internal_torus_radius))
