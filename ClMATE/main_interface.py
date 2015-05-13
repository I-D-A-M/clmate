from PyQt4 import QtGui, QtCore
from .helpers import class_view
import sqlite3


class OverviewWidget(QtGui.QWidget):
    def __init__(self, session_details):
        super(OverviewWidget, self).__init__()

        self.session_details = session_details
        username = self.session_details["username"]
        permissionLevel = self.session_details["permissionLevel"]
        DBname = self.session_details["DBname"]

        #  Set up the main window interface: stack layout managed by a tab bar
        self.stackLayout = QtGui.QStackedLayout()
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.stackLayout)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.switcher = QtGui.QTabBar()
        self.switcher.setStyleSheet(
                            '''QWidget::tab {
                                    background-color: lightGrey;
                                    border: 1px solid grey;
                                    border-bottom-left-radius: 5px;
                                    border-bottom-right-radius: 5px;
                                    margin-bottom: 4px;}
                               QWidget::tab:selected {
                                    background-color: white;
                                    border-top-color: white;
                                    margin-left: -2px;
                                    margin-right: -2px;
                                    margin-bottom: 0px;}''')
        self.switcher.setShape(QtGui.QTabBar.TriangularSouth)

        # For each class assigned to the current login,
        # retrieve class details and populate the overview widget
        DB = sqlite3.connect(DBname)
        with DB:
            DB.row_factory = sqlite3.Row
            ID_query = "select staff_code from staff where username = ?"
            staffID = DB.execute(ID_query, (username,)).fetchone()['staff_code']
            if staffID == 'SU':
                set_query = "select distinct teaching_set from staffing"
                setlist = DB.execute(set_query).fetchall()
            else:
                set_query = "select teaching_set from staffing where staff_code = ?"
                setlist = DB.execute(set_query, (staffID,)).fetchall()
        DB.close()

        for currentset in setlist:
            global current_set
            current_set = currentset[0]
            currentClass = class_view(currentset, self.session_details)
            self.switcher.addTab(current_set)
            self.stackLayout.addWidget(currentClass)
        self.mainLayout.addWidget(self.scrollArea)
        self.mainLayout.addWidget(self.switcher)
        self.setLayout(self.mainLayout)
        self.switcher.connect(self.switcher,
                              QtCore.SIGNAL("currentChanged(int)"),
                              self.tabSwitch)

    def tabSwitch(self):
        # This function will take the current tab index and
        # matches the central widget index to it
        self.stackLayout.setCurrentIndex(self.switcher.currentIndex())
