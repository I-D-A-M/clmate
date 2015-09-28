__all__ = ["bases", "data_entry", "login", "main_w", "analysis", "creators", "helpers",
           "definitions", "main_interface", "admin_panel"]

'''{--External Modules--}'''
import matplotlib
matplotlib.use("Agg")

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from openpyxl import Workbook, load_workbook
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import subprocess
import matplotlib
import sys
import os


# -- Find Python and library versions
#    Using version_info rather than version as that returns
#    a giant string with additional information!

major = str(sys.version_info.major)
minor = str(sys.version_info.minor)
micro = str(sys.version_info.micro)
version = major + '.' + minor + '.' + micro

lib_vers = '\nWith Pandas version ' + pd.__version__
lib_vers += ' - Numpy version ' + np.__version__
lib_vers += ' - Matplotlib version ' + matplotlib.__version__

py_v_message = "Currently running under Python version " + version + lib_vers

################################################################################


'''{--Internal ClMATE Imports--}'''
from .definitions import *
from .login import LoginBox
from .main_w import MainWindow, ActionBar
from .bases import StdWindow
