from __future__ import annotations
from typing import Final, List, Dict, Iterable, Set
from utils import *


@dataclass
class SpectrumBaseItem:
    x: float
    y: float
    y_err: float


def get_interval_index_log(value: float, value_interval: Interval2D, num_of_intervals: int) -> int:
    """Returns the index of the value interval corresponding to the given value. 
    The whole value interval is in a log10 scale

    Args:
        value (float): energy withing the interval
        value_interval (Interval2D): Full value interval
        num_of_intervals (int): number of bins

    Returns:
        int: the value interval index
    """
    return round(num_of_intervals * (np.log(value/value_interval.left))/(np.log(value_interval.right/value_interval.left)))


class SpectrumBase:
    """Represents a spectrum with:

        x: the x coordinate values, for example energy

        y: the spectrum values, for example flux-density

        y_err: the error on y values, for example the standard deviation

    The user has to determine the meaning and units of x and y.

    The spectrum is also iterable.
    """

    def __init__(self, x: Iterable[float],
                 y: Iterable[float],
                 y_err: Iterable[float]):
        """Creates an instance of the class.

        Args:
            x (Iterable[float]): the x coordinate values, for example energy
            y (Iterable[float]): the spectrum values, for example flux-density
            y_err (Iterable[float]): the error on y values, for example the standard deviation
        """
        if len(x) == len(y) == len(y_err):
            self.x = x
            self.y = y
            self.y_err = y_err
            self.length = len(x)
            self.pos = 0
        else:
            raise ValueAndError('The length of x,y, and y_err must be equal!')

    def __next__(self):
        pos = self.pos
        if pos < self.length:
            self.pos += 1
            return self.x[pos], self.y[pos], self.y_err[pos]
        else:
            self.pos = 0
            raise StopIteration

    def __iter__(self):
        return self

    def __getitem__(self, index: int) -> SpectrumBaseItem:
        return SpectrumBaseItem(x=self.x[index], y=self.y[index], y_err=self.y_err[index])

    def __len__(self) -> int:
        return len(self.x)

    def components(self) -> Tuple[Iterable[float], Iterable[float], Iterable[float]]:
        """Returns a tuple with the copy of
        the x, y and y_err components
        of the spectrum

        Returns:
            Tuple[Iterable[float], Iterable[float], Iterable[float]]: x,y,y_err
        """
        return self.x, self.y, self.y_err

    def algebraic_area(self):
        return np.trapz(x=self.x, y=self.y)

    def algebraic_area_err(self):
        return np.sqrt(np.trapz(x=self.x, y=self.y_err**2))

    def get_cpy_on_interval(self, energy_interval: EnergyInterval):
        """Returns the portion of the spectrum on the given interval

        Args:
            left (float): left value of the interval
            right (float): right value of the interval

        Returns:
            SpectrumBase: portion of the spectrum on [left, right]
        """
        cpy = self._get_cpy_on_interval(
            energy_interval.left, energy_interval.right, None)

        return type(self)(x=cpy.x, y=cpy.y, y_err=cpy.y_err)

    def _get_cpy_on_interval(self, left: float, right: float = None, hole: bool = None):
        """
        This function returns the spectrum on the given interval.

        If the right parameter is not passed and hole=True, then the right
        energy bound will be so that the height at that point
        is not greater than the height at the first point, else
        the resulting spectrum will contain all the right points
        starting at the left point.
        """

        x, y, y_err = self.x, self.y, self.y_err

        new_x = []
        new_y = []
        new_y_err = []
        zipped = zip(x, y, y_err)
        if right != None:
            for x_i, y_i, y_err in zipped:
                if(left <= x_i <= right):
                    new_x += [x_i]
                    new_y += [y_i]
                    new_y_err += [y_err]
        elif hole:
            max_height = 0
            for x_i, y_i, y_err in zipped:
                if left <= x_i:
                    if(max_height > 0 and y_i >= max_height):
                        break
                    new_x += [x_i]
                    new_y += [y_i]
                    new_y_err += [y_err]
                    if(max_height <= 0):
                        max_height = new_y[0]

        elif hole == False:
            max_height = 0
            for x_i, y_i, y_err in zipped:
                if left <= x_i:
                    if(max_height > 0 and y_i <= max_height):
                        break
                    new_x += [x_i]
                    new_y += [y_i]
                    new_y_err += [y_err]

                    if(max_height <= 0):
                        max_height = new_y[0]

        return SpectrumBase(np.array(new_x), np.array(new_y), np.array(new_y_err))

    def average_y(self, energy_interval: EnergyInterval) -> float:
        subspectrum = self.get_cpy_on_interval(energy_interval)
        return np.sum(subspectrum.y)/len(subspectrum.y)

    def average(self, energy_interval: EnergyInterval = None) -> Tuple[ValueAndError, float]:

        if energy_interval == None:
            energy_interval = EnergyInterval(self.x[0], self.x[-1])

        subspectrum = self.get_cpy_on_interval(energy_interval)

        aver_x = np.sum(subspectrum.x)/len(subspectrum.x)
        index = get_interval_index_log(aver_x, Interval2D(
            energy_interval.left, energy_interval.right), len(subspectrum.x))
        aver_y = np.sum(subspectrum.y)/len(subspectrum.y)
        aver_y_err = np.sqrt(np.sum(subspectrum.y_err**2)) / \
            len(subspectrum.y_err)

        return ValueAndError(value=aver_y, err=aver_y_err), subspectrum.x[index]

    def std_y(self, energy_interval: EnergyInterval) -> float:
        return np.std(self.get_cpy_on_interval(energy_interval).y)

    def x_interval(self):
        return self.x[0], self.x[-1]