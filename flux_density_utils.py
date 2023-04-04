from spectrum_utils import *
from typing import Final, List, Dict, Iterable, Set
from colum_density_utils import ColumnDensityDistribution
from agn_utils import agn_solid_angle

FULL_TORUS_ANGLE_DEG = AngularInterval(0, 90)

FULL_TORUS_SOLID_ANGLE = agn_solid_angle(
    FULL_TORUS_ANGLE_DEG.from_deg_to_rad())


@dataclass
class NormalizationFluxDensityParameters:
    energy_norm_value: float
    energy_interval: EnergyInterval
    solid_angle: float


SIMULATION_NORM_ENERGY_EV = 1_000
SIMULATION_ENERGY_INTERVAL_EV = EnergyInterval(100, 300_000)

NORMALIZATION_SIMULATION_PARAMS = NormalizationFluxDensityParameters(energy_norm_value=SIMULATION_NORM_ENERGY_EV,
                                                                     solid_angle=FULL_TORUS_SOLID_ANGLE,
                                                                     energy_interval=SIMULATION_ENERGY_INTERVAL_EV)


def build_log10_energy_widths(energy_interval: EnergyInterval, n_intervals: int) -> np.ndarray:
    """Builds a logarithmic list of the widths of the energy intervals [E_{i+1} - E_i]

    The intervals E_1, E_2, ... are logarithmically distributed between 
    the given energy_interval range, using n_intervals intervals.


    Example:

    print(len(build_log10_energy_widths(EnergyInterval(100, 300_000), 2000)))


    Returns:
        np.ndarray: List of energy interval widths
    """

    hv_left, hv_right = energy_interval.left, energy_interval.right

    d_nh_expo = (np.log10(hv_right)-np.log10(hv_left))/n_intervals
    hv_list = []

    for i in range(n_intervals):
        hv_list += [hv_left*(10**(d_nh_expo*(i+1)) - 10**(d_nh_expo*i))]

    return np.array(hv_list)


def get_normalization_factor(norm_params: NormalizationFluxDensityParameters, norm_spectrum: SpectrumCount, energy_widths: np.ndarray):
    index = get_interval_index_log(
        value=norm_params.energy_norm_value,
        value_interval=norm_params.energy_interval,
        num_of_intervals=len(norm_spectrum))

    norm_energy_width = energy_widths[index]
    norm_spectrum_count = norm_spectrum[index].y
    norm_solid_angle = norm_params.solid_angle

    # print(index)
    # print(norm_spectrum_count)
    # print(norm_energy_width)
    # print(norm_solid_angle)

    return (norm_solid_angle*norm_energy_width)/norm_spectrum_count


def agn_solid_angle(alpha: AngularInterval) -> float:
    """Returns the doubled solid angle for
    the corresponding agn viewing angular interval

    Args:
        theta (AngularInterval) 

    Returns:
        float: the solid angle
    """
    solid_angle_up = solid_angle(alpha.beg)
    solid_angle_base = solid_angle(alpha.beg+alpha.length)
    return 2*(solid_angle_base - solid_angle_up)


class FluxDensity(SpectrumBase):
    def __init__(self, x: Iterable[float],
                 y: Iterable[float],
                 y_err: Iterable[float]) -> None:

        super().__init__(x, y, y_err)

    # def _flux_std(self, base: int = 10):
    #     energy_interval = EnergyInterval(*self.x_interval())

    #     energy_widths = build_energy_widths(
    #         energy_interval=energy_interval, num_of_intervals=len(self.x), base=base)

    #     return np.sqrt(np.sum((self.y_err*energy_widths)**2))

    # def flux(self, base_of_log_energy_interval: int = 10):
    #     return ValueAndError(value=self.algebraic_area(),
    #                          err=self._flux_std(base=base_of_log_energy_interval))


class FluxDensityBuilder:

    @staticmethod
    def build_flux_density_for_given_nh(spectrum_count: SpectrumCount,
                                        norm_spectrum: SpectrumCount,
                                        angle_interval: AngularInterval,
                                        nh: float,
                                        nh_distribution: ColumnDensityDistribution,
                                        norm_params: NormalizationFluxDensityParameters = NORMALIZATION_SIMULATION_PARAMS)->FluxDensity:
        """Builds the flux density.

                DONT USE THIS METHOD TO CREATE THE NORMALIZATION FLUX DENSITY!
                The normalization of the Normalization-Flux-Density is different.

        Args:
            spectrum_count (SpectrumCount): This spectrum count is made out of ALL components that count for the given flux density.
            norm_spectrum (SpectrumCount): This is the normalization spectrum, which normally it is the source spectrum.
            angle_interval (AngularInterval): Angle interval at which the given spectral components were taken
            norm_params (NormalizationFluxDensityParameters): Normalization parameters. Typically these should be global (use the default value).

        Returns:
            FluxDensity: The normalized flux density.
        """

        energy_widths = build_log10_energy_widths(energy_interval=norm_params.energy_interval,
                                                  n_intervals=len(norm_spectrum))

        norm_factor = get_normalization_factor(
            norm_params, norm_spectrum, energy_widths)

        solid_angle_ = FluxDensityBuilder._get_solid_angle(angle_interval)

        true_solid_angle = nh_distribution.get_distribution_value_for_nh(
            nh=nh) * solid_angle_

        return FluxDensity(spectrum_count.x,
                           spectrum_count.x*spectrum_count.y*norm_factor /
                           true_solid_angle/energy_widths,
                           spectrum_count.x*spectrum_count.y_err*norm_factor/true_solid_angle/energy_widths)

    @staticmethod
    def build_norm_flux_density(
            norm_spectrum: SpectrumCount,
            angle_interval: AngularInterval,
            norm_params: NormalizationFluxDensityParameters = NORMALIZATION_SIMULATION_PARAMS):
        """Builds the normalization flux density.

        Args:
            norm_spectrum (SpectrumCount): This is the normalization spectrum, which normally it is the source spectrum.
            angle_interval (AngularInterval): Angle interval at which the given spectral components were taken
            norm_params (NormalizationFluxDensityParameters): Normalization parameters. Typically these should be global (use the default value).

        Returns:
            _type_: _description_
        """

        energy_widths = build_log10_energy_widths(energy_interval=norm_params.energy_interval,
                                                  n_intervals=len(norm_spectrum))

        norm_factor = get_normalization_factor(
            norm_params, norm_spectrum, energy_widths)

        solid_angle_ = FluxDensityBuilder._get_solid_angle(angle_interval)

        true_solid_angle = solid_angle_

        return FluxDensity(norm_spectrum.x,
                           norm_spectrum.x*norm_spectrum.y*norm_factor /
                           true_solid_angle/energy_widths,
                           norm_spectrum.x*norm_spectrum.y_err*norm_factor/true_solid_angle/energy_widths)

    @staticmethod
    def _get_solid_angle(angle_interval: float):
        return agn_solid_angle(angle_interval)
