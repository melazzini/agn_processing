from spectrum_utils import *
from colum_density_utils import *

empty_spectrum = PoissonSpectrumCountFactory.build_log_empty_spectrumcount(100,300_000,2000)

empty_spectrum[1997].y=777
empty_spectrum[1997].y_err=12

for item in empty_spectrum:
    print(item)

print(empty_spectrum[-1])