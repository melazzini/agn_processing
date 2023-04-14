from colum_density_utils import ValueAndError, ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt
from typing import Dict, List
from agn_simulation_policy import AGN_NH_AVERAGE
from measurable_utils import get_ew_vs_n_aver


g = ColumnDensityGrid(left_nh=LEFT_NH, right_nh=RIGHT_NH,
                      n_intervals=NH_INTERVALS)

data: Dict[int, List[ValueAndError]] = get_ew_vs_n_aver(
    f"/home/francisco/Projects/agn/agn_processing/results/{g.n_intervals}_{g.left:0.2g}_{g.right:0.2g}.measurements", nh_index=g.index(5e23), a_fe='1xfe')

for n_aver_key in data:
    for ew in data[n_aver_key]:
        plt.scatter(n_aver_key, ew.value)

plt.show()
