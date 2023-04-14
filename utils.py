from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Iterable
from abc import abstractmethod, ABC

Vector1d = List[float]
"""List of numbers or similar like a 1d-ndarray object."""

DEFAULT_EPSILON = 1E-12
"""this is the default precision that we use in our calculations"""

LENGTH = 'L'
TIME = 'T'
MASS = 'M'
TEMPERATURE = 'K'
ANGLE = 'A'
ENERGY = 'ML2T-2'
N_H_DIM = '_N_H_'


def solid_angle(half_opening_angle: float) -> float:
    """Returns the solid angle that corresponds
    to the given half-opening angle.

    For example if the HOA is pi/2 then the function
    returns 2pi as the solid angle.

    Args:
        half_opening_angle (float): 

    Returns:
        float: the corresponding solid angle
    """
    return 2*np.pi*(1.0 - np.cos(half_opening_angle))


def solid_angle_doubled(half_opening_angle: float) -> float:
    """Returns the doubled solid angle that corresponds
    to the given half-opening angle.

    Args:
        half_opening_angle (float): 

    Returns:
        float: The doubled solid angle
    """
    return 2.0 * solid_angle(half_opening_angle)


def x_y(path: str, index_left: int = 0, index_right: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Builds a pair of np ndarrays using the input file, which is in the form
    of a white-space separated columns, for example:
                    1\t   0.1  \t   0 \n
                    2\t   0.2  \t   0 \n
                    3\t   0.3  \t   1 \n
                    4\t   0.9  \t   0 \n

    The file can have more that two columns, but the length of the 
    columns must be the same!

    Args:
        path (str): the path to the input file that contains the data
        index_left (int, optional): the index of the x-column in the file. Defaults to 0 (ie the first column).
        index_right (int, optional): the index of the y-column in the file . Defaults to 1 (ie the second column).

    Returns:
        tuple(np.ndarray,np.ndarray): x, y ndarrays correspondingly
    """
    try:  # normal case of multiple lines
        data = np.loadtxt(path)
        return data[:, index_left], data[:, index_right]
    except:  # case of only one single line in the file, for example: -1 50.92 30
        data = np.loadtxt(path)
        return np.array([data[index_left]]), np.array([data[index_right]])


def x_y_z(path: str, index_left: int = 0, index_mid: int = 1, index_right: int = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Builds three np ndarrays using the input file, which is in the form
    of a white-space separated columns, for example:
                    1\t   0.1  \t   0 \n
                    2\t   0.2  \t   0 \n
                    3\t   0.3  \t   1 \n
                    4\t   0.9  \t   0 \n

    The file can have more that three columns, but the length of the 
    columns must be the same!

    Args:
        path (str): the path to the input file that contains the data
        index_left (int, optional): the index of the x-column in the file. Defaults to 0 (ie the first column).
        index_mid (int, optional): the index of the y-column in the file . Defaults to 1 (ie the second column).
        index_right (int, optional): the index of the z-column in the file . Defaults to 2 (ie the third column).

    Returns:
        tuple(np.ndarray, np.ndarray, np.ndarray): x,y,z ndarrays correspondingly
    """

    try:  # normal case of multiple lines
        data = np.loadtxt(path)
        return data[:, index_left], data[:, index_mid], data[:, index_right]
    except:  # case of only one single line in the file, for example: -1 50.92 30
        data = np.loadtxt(path)
        return np.array([data[index_left]]), np.array([data[index_mid]]), np.array([data[index_right]])


def mean_2d(x_ar: Vector1d, y_ar: Vector1d) -> Tuple[float, float]:
    """Get the mean of two 1d-Vectors at the same time.

    The length of both vectors must be same!

    Args:
        x_ar (Vector1d): x-Vector, for example [1,2,3]
        y_ar (Vector1d): y-Vector, for example [0,1,2]

    Raises:
        ValueError: if the lengths of the vectors is different.

    Returns:
        Tuple[float, float]: mean of the x-vector, mean of the y-vector
    """
    if(len(x_ar) != len(y_ar)):
        raise ValueError("the length of the arrays must be equal!")
    return np.mean(x_ar), np.mean(y_ar)


@dataclass
class ValueAndError:
    value: float
    err: float


@dataclass
class Interval2D:
    left: float
    right: float

    def __contains__(self, value: float) -> bool:
        if self.left < self.right:
            if self.left <= value <= self.right:
                return True
            else:
                return False
        else:
            if self.left >= value >= self.right:
                return True
            else:
                return False


class EnergyInterval(Interval2D):
    pass


class AngularInterval(Interval2D):
    """Represents an angular interval.
    """

    def __init__(self, beg: float, length: float):
        """Creates an instance with the staring
        angle and the length of it.

        You have to keep in mind the units that
        you are using, because this information
        is not kept in the created object.

        Args:
            beg (float): the starting angle
            length (float): the length of the interval
        """
        self.beg = beg
        self.length = length
        self.end = self.beg + self.length
        super().__init__(left=self.beg, right=self.end)

    def from_deg_to_rad(self) -> AngularInterval:
        """Translates from degrees to radians the angular interval.

        Here it's assumed that the initial units
        are degrees.

        Returns:
            AngularInterval: self
        """
        # self.beg = np.radians(self.beg)
        # self.length = np.radians(self.length)
        return AngularInterval(beg=np.radians(self.beg), length=np.radians(self.length))

    def from_rad_to_deg(self) -> AngularInterval:
        """Translates from radians to degrees the angular interval.

        Here it's assumed that the initial units
        are radians.

        Returns:
            AngularInterval: self
        """
        self.beg = np.degrees(self.beg)
        self.length = np.degrees(self.length)
        return self

    def __str__(self):
        return f'({self.beg}, {self.length})'


class UnitsPolicy(ABC):

    @abstractmethod
    def translate_energy(self, value: float) -> float:
        pass

    @abstractmethod
    def translate_length(self, value: float) -> float:
        pass

    @abstractmethod
    def translate_angle(self, value: float) -> float:
        pass


@dataclass
class Histo:
    """This class represents a histogram.

    This class holds the raw data, because this
    is usually convenient for different calculations.

    Plus it provides basic statistical methods: mean and std.
    """
    bins: np.ndarray
    counts: np.ndarray
    counts_err: np.ndarray
    raw_data: np.ndarray

    def mean(self) -> float:
        """Get the mean of the raw data described by the histogram.

        This value is calculated every time you call this method.
        Thus: 
                Cache this value for performance!

        Returns:
            float: mean value of the raw data.
        """

        return np.mean(self.raw_data)

    def std(self) -> float:
        """Get the std of the raw data described by the histogram.

        This value is calculated every time you call this method.
        Thus: 
                Cache this value for performance!

        Returns:
            float: standard deviation of the raw data.
        """
        mean_ = self.mean()
        n = len(self.raw_data)
        return np.sqrt(sum(((self.raw_data-mean_)**2)/n))/mean_


def product_transport_err(data: Iterable[ValueAndError]) -> float:
    """Get the error of a product or division.

    Args:
        data (Iterable[ValueAndError]): list of ValueAndError to calculate the total error.

    See: https://studfile.net/preview/3130553/page:4/

    Returns:
        float: error
    """
    return sum([(item.err/item.value)**2 for item in data])**0.5



def chi2(observed, expected):
    return np.sum(((observed-expected)**2)/expected)