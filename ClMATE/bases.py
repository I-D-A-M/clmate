from PyQt4 import QtGui, QtCore
from .definitions import window_heading

class StdWindow(QtGui.QWidget):
    '''
    Default window layout within ClMATE. This sets the window icon and defines
    a centre method that places the window in the centre of the screen.
    '''
    def __init__(self):
        super(StdWindow, self).__init__()

    def initUI(self):
        '''
        Initialise the window frame and position.
        '''
        self.center()

        self.setWindowTitle(window_heading)
        icon = QtGui.QIcon('ClMATE/resources/logo.png')
        self.setWindowIcon(icon)
        QtGui.QToolTip.setFont(QtGui.QFont('Source Sans Pro', 14))
        self.show()

    def center(self):
        '''
        Find the desktop dimensions of the user's machine and
        centre the window accordingly.
        '''
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class QIComboBox(QtGui.QComboBox):
    '''
    An overridden version of a PyQt QComboBox that allows for the current
    displayed text to be registered as a field within a QWizard object.
    '''
    def __init__(self, parent=None):
        super(QIComboBox, self).__init__(parent)

    @QtCore.pyqtProperty(str)
    def currentItemData(self):
        return str(self.currentText())
