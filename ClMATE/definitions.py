'''
-- Author:       I D A Morrison
-- Twitter:      @MrMorrisonMaths
-- PyVersion:    Python3.x
-- Dependencies: PyQt4
'''
from PyQt4 import QtGui

################################################################################
# Program wide definitions #
############################

window_heading = 'ClMATE 2.0'
program_version = '2.0.5.2'
DBname = 'ClMATE_DB.db'
export_path = "R:\\ClMATE2.0\\ClMATE_output_files\\"
QBOX_SIZE = 30
ICON_SIZE = 40
TOOLBAR_SIZE = 73

DEFAULT_PLOT_WIDTH = 8
DEFAULT_PLOT_HEIGHT = 5
DEFAULT_PLOT_DPI = 100
plot_style = 'barh'

grey = QtGui.QColor(90, 90, 90, 255)
dGrey = QtGui.QColor(20, 20, 20, 255)
white = QtGui.QColor(255, 255, 255, 255)
black = QtGui.QColor(0, 0, 0, 255)

red = QtGui.QColor(255, 97, 97, 255)
green = QtGui.QColor(175, 238, 193, 255)
orange = QtGui.QColor(238, 224, 175, 255)
purple = QtGui.QColor(225, 176, 238, 255)
# pink = QtGui.QColor(255, 204, 217, 255)
