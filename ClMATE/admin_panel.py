from .data_entry import InputWindow
from .bases import StdWindow
from PyQt4 import QtGui, QtCore
import sqlite3

class AdminPanel(StdWindow):
    def __init__(self, session_details):
        super(AdminPanel, self).__init__()

        self.session_details = session_details
        DBname = self.session_details["DBname"]
        DB = sqlite3.connect(DBname)

        #  Set up the main window interface: stack layout managed by a tab bar
        self.stackLayout = QtGui.QStackedLayout()
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.stackLayout)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        # Need to look at showing a dynamic message...
        self.statusBar = QtGui.QStatusBar()
        self.statusBar.showMessage(
                "This message can be set in the main_interface file")
        self.mainLayout = QtGui.QVBoxLayout()
        self.switcher = QtGui.QTabBar()
        # Create a tab for each course and display the staffing of that course
        ID_query = "select distinct course_ID from courses"
        courseIDs = DB.execute(ID_query).fetchall()
        for ID in courseIDs:
            global course_class_overview
            query = ("select course_title from courses "
                     "where course_ID = ? limit 1")
            self.current_course = DB.execute(query, (ID[0],)).fetchall()[0][0]
            course_class_overview = self.course_overview()
            self.switcher.addTab(self.current_course)
            self.stackLayout.addWidget(course_class_overview)
        self.mainLayout.addWidget(self.switcher)
        self.mainLayout.addWidget(self.scrollArea)
        self.mainLayout.addWidget(self.statusBar)
        self.setLayout(self.mainLayout)
        self.switcher.connect(self.switcher,
                              QtCore.SIGNAL("currentChanged(int)"),
                              self.tabSwitch)
        self.resize(500, 500)
        self.setWindowTitle('Admin Panel')
        self.show()

    def tabSwitch(self):
        # This function will take the current tab index and
        # matches the central widget index to it
        self.stackLayout.setCurrentIndex(self.switcher.currentIndex())

    def course_overview(self):
        DBname = self.session_details["DBname"]
        DB = sqlite3.connect(DBname)
        overview= QtGui.QGroupBox('Select a class to enter data for: ')
        vbox = QtGui.QVBoxLayout()
        query = "select distinct teaching_set from staffing where course = ?"
        setlist = DB.execute(query, (self.current_course,)).fetchall()
        for currentset in setlist:
            current_set = currentset[0]
            query = "select staff_code from staffing where teaching_set = ?"
            codes = DB.execute(query, (current_set,)).fetchall()
            label_text = current_set + '  Staff: '
            for code in codes:
                label_text += code[0]
                label_text += ' '
            select_button = QtGui.QRadioButton(label_text)
            vbox.addWidget(select_button)
        input_start = QtGui.QPushButton('Enter data')
        input_start.clicked.connect(self.launch_input)
        vbox.addWidget(input_start)
        overview.setLayout(vbox)
        return overview

    def launch_input(self):
        DBname = self.session_details["DBname"]
        DB = sqlite3.connect(DBname)
        box = self.stackLayout.currentWidget().layout()
        for n in range(box.count()-1):
            if box.itemAt(n).widget().isChecked():
                label = box.itemAt(n).widget().text()
                className = label.split('  Staff:')
                # -- open an input window
                global input_screen, overviewWidget
                # -- Locate assessment data
                CHOSEN_CLASS = className[0]
                query = "select count(*) from cohort where teaching_set = ?"
                CLASS_SIZE = DB.execute(query, (str(CHOSEN_CLASS),)).fetchone()
                query = "select aName from assignedTests where teaching_set = ?"
                assessments = DB.execute(query, (str(CHOSEN_CLASS),)).fetchall()
                # -- Warn the user if there are no assigned assessments
                if len(assessments) == 0:
                    failure = QtGui.QMessageBox.question(
                                        self,
                                        'Warning!',
                                        "No assessments found for this class.")
                    return -1
                # -- Populate the assessment list and swap out
                #    the overview screen for the input screen
                CHOSEN_ASSESSMENTS = []
                for a in range(len(assessments)):
                    CHOSEN_ASSESSMENTS.append(str(assessments[a][0]))
                input_screen = InputWindow(self.session_details,
                                           CHOSEN_CLASS,
                                           CLASS_SIZE,
                                           CHOSEN_ASSESSMENTS)
                main_window = self.session_details["main_window"]
                main_window.setCentralWidget(input_screen)
                self.close()
