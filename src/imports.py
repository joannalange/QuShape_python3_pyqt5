
__version__ = "1.0"

import os
import platform
import sys
import numpy as np
import shelve

from PyQt4 import QtCore,QtGui, Qt

import time
import webbrowser
    
### IMPORT MATPLOT
import matplotlib 
matplotlib.use('Qt4Agg')
#if matplotlib.get_backend() != 'agg':
#    matplotlib.use('agg')   
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
#from matplotlib.widgets import MultiCursor,SpanSelector
from matplotlib.pyplot import setp
from matplotlib.patches import ConnectionPatch,Rectangle
from matplotlib import rcParams
from matplotlib.text import Text

#from Functions import *
#import dlgHelp

#import qrc_resources

import warnings
warnings.simplefilter('ignore', np.RankWarning)
np.seterr(all='ignore')

  
#from dlgTool import *
from Dialogs import *
from drawClass import *   
