from spectrum_utils import *
from colum_density_utils import *


index = get_interval_index_log(value=1.75e24, value_interval=ColumnDensityInterval(
    LEFT_NH, RIGHT_NH), num_of_intervals=NH_INTERVALS)
# print(index)

d_nh_expo = (np.log10(RIGHT_NH)-np.log10(LEFT_NH))/NH_INTERVALS

nh_left = LEFT_NH

nh_list = []

for i in range(NH_INTERVALS):
    nh_ip1 = LEFT_NH*10**(d_nh_expo*(i+1))
    nh_i = LEFT_NH*10**(d_nh_expo*i)
    d_nh = nh_ip1 - nh_i
    nh_list += [nh_i + (d_nh/2)]


# print(nh_list)
# print(len(nh_list))

nh_bounds = np.logspace(np.log10(LEFT_NH), np.log10(RIGHT_NH), NH_INTERVALS+1)

for i, nh_left_val in enumerate(nh_bounds[:-1]):
    nh_i = (nh_left_val+nh_bounds[i+1])/2
    # print(f'#{i+1:>2} N_H={nh_i:0.3e}cm-2')
    interval = ColumnDensityInterval(left=nh_left_val, right=nh_bounds[i+1])
    # print(interval)


nh_grid = ColumnDensityGrid(left_nh=1e22, right_nh=2e24, n_intervals=30)

print(nh_grid.index(nh=1e23))

