__version__ = "1.0"

### IMPORT MATPLOT
import matplotlib
import numpy as np

matplotlib.use('Qt4Agg')
# if matplotlib.get_backend() != 'agg':
#    matplotlib.use('agg')
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# from matplotlib.widgets import MultiCursor, SpanSelector

# from Functions import *
# import dlgHelp

# import qrc_resources

import warnings

warnings.simplefilter('ignore', np.RankWarning)
np.seterr(all='ignore')

# from dlgTool import *
