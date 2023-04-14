from colum_density_utils import ValueAndError, ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt
from typing import Dict, List
from agn_simulation_policy import AGN_NH_AVERAGE
from measurable_utils import get_shoulder_vs_nhaver


g = ColumnDensityGrid(left_nh=LEFT_NH, right_nh=RIGHT_NH,
                      n_intervals=NH_INTERVALS)

data: Dict[str, List[ValueAndError]] = get_shoulder_vs_nhaver(
    f"/home/francisco/Projects/agn/agn_processing/results/{g.n_intervals}_{g.left:0.2g}_{g.right:0.2g}.measurements")

for nh_key in data:
    for shoulder in data[nh_key]:
        plt.scatter(AGN_NH_AVERAGE[nh_key], shoulder.value)

plt.show()
