from colum_density_utils import DEFAULT_NH_GRID
from typing import Final, Dict

ABUNDANCE_COLOR = {
    '05xfe': 'peru',
    '07xfe': 'magenta',
    '1xfe': 'cyan',
    '15xfe': 'gray',
    '2xfe': 'blue',
}

NH_COLORS = {
    DEFAULT_NH_GRID.index(nh=1e22): 'red',
    DEFAULT_NH_GRID.index(nh=2e22): 'orange',
    DEFAULT_NH_GRID.index(nh=5e22): 'lime',
    # DEFAULT_NH_GRID.index(nh=8e22): 'orange',
    DEFAULT_NH_GRID.index(nh=1e23): 'gold',
    DEFAULT_NH_GRID.index(nh=2e23): 'brown',
    DEFAULT_NH_GRID.index(nh=5e23): 'green',
    DEFAULT_NH_GRID.index(nh=1e24): 'pink',
}




NH_LABELS = {
    DEFAULT_NH_GRID.index(nh=1e22): r'$10^{22} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=2e22): r'$2 \times 10^{22} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=5e22): r'$5 \times 10^{22} cm^{2}$',
    # DEFAULT_NH_GRID.index(nh=8e22): r'$8 \times 10^{22} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=1e23): r'$10^{23} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=2e23): r'$2 \times 10^{23} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=5e23): r'$5 \times 10^{23} cm^{2}$',
    DEFAULT_NH_GRID.index(nh=1e24): r'$10^{24} cm^{2}$',
}


NUM_OF_CLOUDS_SMOOTH = -1


MARKERS: Final[Dict[int, str]] = {2: '<', 3: '>',
                                  4: '^', 5: '*', 6: 's', 8: 'v', 10: 'p',
                                  NUM_OF_CLOUDS_SMOOTH: 'o', }
