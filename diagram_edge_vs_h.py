from measurable_utils import get_edge_vs_h
from colum_density_utils import ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt

g = ColumnDensityGrid(LEFT_NH, RIGHT_NH, NH_INTERVALS)

h, _, edge, _ = get_edge_vs_h(
    f"/home/francisco/Projects/agn/agn_processing/results/{g.n_intervals}_{g.left:0.2g}_{g.right:0.2g}.measurements", nh_index=g.index(5e23))

plt.scatter(h, 1-edge)

plt.show()
