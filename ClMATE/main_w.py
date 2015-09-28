'''
-- Author:       I.D.A-M
-- Twitter:      @InnesMorrison
-- PyVersion:    Python3.x
-- Dependencies: PyQt4
'''
from PyQt4 import QtGui, QtCore
from .definitions import window_heading, ICON_SIZE, TOOLBAR_SIZE
from .main_interface import OverviewWidget
from .admin_panel import AdminPanel
from .data_entry import InputWindow
from .creators import *
from .analysis import *
import sqlite3
import time


class MainWindow(QtGui.QMainWindow):
    '''
    This class defines and manages the main window including displaying/editing
    assessment data; setting assessments and running reports.
    '''
    def __init__(self):
        super(MainWindow, self).__init__()

    def initUI(self, session_details=dict()):
        self.session_details = session_details
        icon = QtGui.QIcon('ClMATE/resources/logo.png')
        self.setWindowIcon(icon)
        self.setWindowTitle(window_heading)

        self.setStyleSheet('''MainWindow {
                            background-color: white;}''')

        ######################################
        self.toolbar = self.addToolBar('Menu Interface')
        Menu = MenuWidget(session_details)
        self.toolbar.addWidget(Menu)
        # -- Prevent the toolbar from being dragged and dropped
        self.toolbar.setMovable(False)

        global overviewWidget
        overviewWidget = OverviewWidget(session_details)
        self.setCentralWidget(overviewWidget)

        screenx = QtGui.QDesktopWidget().availableGeometry().width()
        screeny = QtGui.QDesktopWidget().availableGeometry().height()
        self.resize(screenx, screeny)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)         # boo for American spellings
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(
            self,
            "Warning!",
            "Are you sure you want to quit?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            with open('clmate_log.txt', 'a') as log:
                username = self.session_details["username"]
                print("--> {} logged off at: {}".format(username, time.ctime()), file=log)
            event.accept()
        else:
            event.ignore()


class MenuWidget(QtGui.QWidget):
    def __init__(self, session_details):
        super(MenuWidget, self).__init__()

        self.session_details = session_details
        permissionLevel = self.session_details["permissionLevel"]
        self.main_window = self.session_details["main_window"]

        MenuFont = QtGui.QFont('Amatic SC', 15, weight=50)
        MenuFont.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(MenuFont)

        classPerformance = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/crowd.png'),
            '&Class Performance',
            self)
        pupilPerformance = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/female192.png'),
            '&Pupil Performance',
            self)
        recordAssessment = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/book135.png'),
            '&Record Assessment',
            self)
        recordAssessment.triggered.connect(self.record_assessments)
        analyseResults = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/person236.png'),
            '&Analysis of Results',
            self)
        analyseResults.triggered.connect(self.analyse_results_cohort)

        if permissionLevel == 'admin':
            adminRecord = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/writing17.png'),
                '&Admin Record Override',
                self)
            adminRecord.triggered.connect(self.admin_record_override)
            manageAssessments = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/homework.png'),
                '&Manage Assessments',
                self)
            newAssessment = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/pens.png'),
                "Create a new assessment",
                self)
            newAssessment.triggered.connect(self.newAssessment)
            newAssessment.setShortcut('Alt+N')
            Aassigner = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/maths2.png'),
                "Assign assessments",
                self)
            Aassigner.triggered.connect(self.aAssigner)
            manageCohort = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/teacher9.png'),
                '&Manage Cohort',
                self)
            # manageCohort.triggered.connect(...)
            manageUsers = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/man337.png'),
                '&Manage Users',
                self)
            # manageUsers.triggered.connect(...)
            manageCourses = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/student13.png'),
                '&Manage Courses',
                self)
            newCourse = QtGui.QAction(
                QtGui.QIcon('ClMATE/resources/books8.png'),
                "Set up a new course",
                self)
            newCourse.triggered.connect(self.newCourse)
            newCourse.setShortcut('Alt+C')

        settings = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/three115.png'),
            '&Settings',
            self)
        about = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/graduation30.png'),
            '&About ClMATE',
            self)
        about.triggered.connect(self.about)
        help_ = QtGui.QAction(
            QtGui.QIcon('ClMATE/resources/umbrella42.png'),
            '&Help',
            self)

        # -- Define and create the actions available for the user
        m_actions = [recordAssessment, classPerformance, pupilPerformance]
        m_labels = ['Enter Results', 'Class Performance', 'Pupil Performace']
        MainActions = ActionBar(m_actions, m_labels)

        if permissionLevel == 'admin':
            ad_actions = [adminRecord, newAssessment, newCourse,
                          Aassigner, manageAssessments, manageCourses,
                          manageUsers, manageCohort]
            ad_labels = ['Admin Results', 'New Assessment', 'New Course',
                         'Set an Assessment', 'Manage Assessments',
                         'Manage Courses', 'Manage Users', 'Manage Cohort']
            AdminActions = ActionBar(ad_actions, ad_labels)

        an_actions = [analyseResults, pupilPerformance, classPerformance]
        an_labels = ['Results Analysis',
                     'Pupil Performance',
                     'Class Performance']
        AnalysisActions = ActionBar(an_actions, an_labels)

        op_actions = [settings]
        op_labels = ['Settings']
        OptionActions = ActionBar(op_actions, op_labels)

        hl_actions = [about, help_]
        hl_labels = ['About ClMATE', 'Help']
        HelpActions = ActionBar(hl_actions, hl_labels)

        #  -- Set up the main window interface: a stack managed by a tab bar
        self.stackLayout = QtGui.QStackedLayout()
        self.stackLayout.setMargin(0)
        self.stackLayout.setSpacing(0)
        self.menuBar = QtGui.QWidget()
        self.menuBar.setFixedHeight(TOOLBAR_SIZE - 2)
        self.menuBar.setLayout(self.stackLayout)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(0)
        self.switcher = QtGui.QTabBar()

        self.switcher.addTab('ClMATE')
        self.stackLayout.addWidget(MainActions)

        if permissionLevel == 'admin':
            self.switcher.addTab('Admin')
            self.stackLayout.addWidget(AdminActions)

        self.switcher.addTab('Analysis')
        self.stackLayout.addWidget(AnalysisActions)
        self.switcher.addTab('Options')
        self.stackLayout.addWidget(OptionActions)
        self.switcher.addTab('Help')
        self.stackLayout.addWidget(HelpActions)

        # -- add tab icons
        self.switcher.setTabIcon(0, QtGui.QIcon('ClMATE/resources/clouds15.png'))
        if permissionLevel == 'admin':
            self.switcher.setTabIcon(1, QtGui.QIcon('ClMATE/resources/circle55.png'))
            self.switcher.setTabIcon(2, QtGui.QIcon('ClMATE/resources/pie56.png'))
            self.switcher.setTabIcon(3, QtGui.QIcon('ClMATE/resources/electronic51.png'))
            self.switcher.setTabIcon(4, QtGui.QIcon('ClMATE/resources/rain33.png'))
        else:
            self.switcher.setTabIcon(1, QtGui.QIcon('ClMATE/resources/pie56.png'))
            self.switcher.setTabIcon(2, QtGui.QIcon('ClMATE/resources/electronic51.png'))
            self.switcher.setTabIcon(3, QtGui.QIcon('ClMATE/resources/rain33.png'))

        self.mainLayout.addWidget(self.switcher)
        self.mainLayout.addWidget(self.menuBar)
        self.setLayout(self.mainLayout)
        self.switcher.connect(self.switcher,
                              QtCore.SIGNAL("currentChanged(int)"),
                              self.tabSwitch)

    def tabSwitch(self):
        # This function will take the current tab index
        # and match the central widget index to it
        self.stackLayout.setCurrentIndex(self.switcher.currentIndex())

    def newCourse(self):
        global newCourse
        newCourse = Course(self.session_details)

    def newAssessment(self):
        global newAssm
        newAssm = Assessment(self.session_details)

    def aAssigner(self):
        global Aassigner
        Aassigner = AssessmentAssigner(self.session_details)

    def record_assessments(self):
        global input_screen
        main_window = self.session_details["main_window"]
        # It looks like simply referring to 'overviewWidget' even when rebound
        # after data input was keeping a reference to the ORIGINAL version not
        # the new one. PyQt deletes a centralWidget when it is swapped out so
        # this was raising a C level error. [LOOK INTO THIS!]
        OV = main_window.centralWidget()
        CHOSEN_CLASS = OV.switcher.tabText(OV.switcher.currentIndex())

        # -- Locate assessment data
        DBname = self.session_details["DBname"]
        DB = sqlite3.connect(DBname)
        with DB:
            query = "select count(*) from cohort where teaching_set = ?"
            CLASS_SIZE = DB.execute(query, (str(CHOSEN_CLASS),)).fetchone()
            query = "select aName from assignedTests where teaching_set = ?"
            assessments = DB.execute(query, (str(CHOSEN_CLASS),)).fetchall()
        # -- Warn the user if there are no currently assigned assessments
        if len(assessments) == 0:
            QtGui.QMessageBox.question(
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
        self.main_window.setCentralWidget(input_screen)

    def analyse_results_cohort(self):
        global analyser
        OV = self.main_window.centralWidget()
        tSet = OV.switcher.tabText(OV.switcher.currentIndex())
        analyser = Analyser(tSet, self.session_details)
        self.main_window.setCentralWidget(analyser)

    def admin_record_override(self):
        global admin_panel
        admin_panel = AdminPanel(self.session_details)

    def about(self):
        QtGui.QMessageBox.question(
            self,
            'About ClMATE',
            ("ClMATE - Close Monitoring and Analysis Tools for Educators\n\n"

             "ClMATE aims to provide teachers with a lightweight, easy to use "
             "interface for recording and analysing pupil attainment data. "
             "Multiple access levels are possible through admin accounts allowing "
             "heads of departments to set and manage courses for their staff. "
             "Initial set up can take a .xlsx output from SIMS.net in order to "
             "automate the import of pupil details. If desired, ClMATE is capable "
             "of exporting results data and analysis in a formatted .xlsx "
             "file for printing and further analysis.\n\n"

             "All data created with ClMATE is kept within a local directory SQLite3 "
             "database. Please note that ClMATE can be run on either Python2.X or "
             "Python3.X provided that all external libraries are present and currently "
             "located in the working directory: no additional installation is required.\n"

             "\nAll work is copyright I.Morrison 2014.\n"
             "Contact: @MrMorrisonMaths [Twitter]\n"

             "\n- External Libraries\n"
             "\nPyQt4:: http://www.riverbankcomputing.co.uk/software/pyqt/download\n"
             "> QtCore and QtGui modules are used to create the GUI interface of ClMATE.\n"
             "\nNumpy:: http://www.numpy.org/\n"
             "> High speed numerical computation.\n"
             "\nPandas:: http://pandas.pydata.org/\n"
             "> Efficient data analysis and manipulation.\n"
             "\nMatplotLib:: http://matplotlib.org/\n"
             "> Plotting and graphical representation of data.\n"
             "\nOpenpyxl:: http://openpyxl.readthedocs.org/en/latest/\n"
             "> Read and write capability for .xls / .xlsx including rich formatting "
             "of the generated spreadsheet. NOTE: openpyxl requires jdcal in order to run."))


class ActionBar(QtGui.QToolBar):
    '''Labelled, stackable toolbar from a list of actions and labels.'''
    def __init__(self, action_list, label_list):
        super(ActionBar, self).__init__()
        for a in enumerate(action_list):
            a[1].setIconText(label_list[a[0]])
            self.addAction(a[1])
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.setFixedHeight(TOOLBAR_SIZE)
        self.setStyleSheet('ActionBar {background-color: white;}')
