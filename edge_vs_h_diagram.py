from finding_nh_utils import get_edge_vs_h
from colum_density_utils import ColumnDensityGrid
from agn_processing_policy import *
import matplotlib.pyplot as plt

g = ColumnDensityGrid(LEFT_NH, RIGHT_NH, NH_INTERVALS)

h, _, edge, _ = get_edge_vs_h(
    "/home/francisco/Projects/agn/agn_processing/results/errors.log", nh_index=g.index(5e23))

plt.scatter(h, 1-edge)

plt.show()
