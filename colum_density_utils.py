from utils import *

LEFT_NH = 1E22
RIGHT_NH = 2E24
NH_INTERVALS = 30


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
