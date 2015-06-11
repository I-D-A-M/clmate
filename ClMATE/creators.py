'''
-- Author:       I D A Morrison
-- Twitter:      @MrMorrisonMaths
-- PyVersion:    Python3.x
-- Dependencies: PyQt4
'''
import os
import sys
import sqlite3
from PyQt4 import QtGui
from .bases import StdWindow, QIComboBox
from .definitions import window_heading


class Assessment(QtGui.QWizard):
    '''
    Step by step set up guide for creating a new assessment and
    assigning to classes. Note that a course must have been

   created prior to running this function and that classes
    must have been assigned to the course in order to set the
    assessment.
    '''
    def __init__(self, session_details):
        super(Assessment, self).__init__()
        self.session_details = session_details
        icon = QtGui.QIcon('ClMATE/resources/logo.png')
        self.setWindowIcon(icon)
        # -- Inform the user of what information they need to continue.
        intro_page = QtGui.QWizardPage()
        intro_page.setTitle("ClMATE Assessment Creator")
        intro_label = QtGui.QLabel(
            "Welcome to the ClMATE assessment creator."
            "\n\nBefore you begin, make sure that you have the following "
            "details at hand:\n\n  Course Title\n  Question Titles\n  "
            "Question questions\n  Marks for each question\n  "
            "File locations for the paper and mark scheme")
        intro_label.setWordWrap(True)
        intro_layout = QtGui.QVBoxLayout()
        intro_layout.addWidget(intro_label)
        intro_page.setLayout(intro_layout)
        # -- Locate and assign a new assessment ID
        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            aID_query = "select aID from assessments order by aID desc limit 1"
            self.aID = DB.execute(aID_query).fetchone()
        DB.close()

        if self.aID:
            self.aID = int(self.aID[0]) + 1
        else:
            self.aID = 1

        ########################################################################

        # -- This page collects the basic details about the assessment
        self.details_page = QtGui.QWizardPage()
        self.details_page.setTitle("Assessment Details")
        self.details_instructions = QtGui.QLabel(
            "Please specify the assessment details and attach "
            "a question paper and a mark scheme:")
        self.details_instructions.setWordWrap(True)
        self.details_nameLabel = QtGui.QLabel("Assessment Name:")
        self.details_nameLineEdit = QtGui.QLineEdit()
        self.details_page.registerField("ASSESSMENT_NAME*",
                                        self.details_nameLineEdit)
        # -- Allows selection of a course currently stored within ClMATE
        self.courseLabel = QtGui.QLabel("Course:")
        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            course_query = "select distinct course_title from courses"
            courses = DB.execute(course_query).fetchall()
        DB.close()

        self.coursebox = QIComboBox(self)
        if courses:
            for course in courses:
                self.coursebox.addItem(course[0])
            self.details_page.registerField("COURSE",
                                            self.coursebox,
                                            "currentItemData")
        else:
            QtGui.QMessageBox.question(
                self,
                'Warning',
                "ClMATE currently has no registered courses. "
                "Please create one now.")
            global create_a_course
            create_a_course = Course()
            self.done()
        # -- Number of questions
        self.numlabel = QtGui.QLabel("Number of questions:")
        self.numspin = QtGui.QSpinBox()
        self.numspin.setMinimum(1)
        self.details_page.registerField("NUMQs", self.numspin)
        # -- Locate and store the path to assessment documents
        self.paper = QtGui.QLineEdit()
        self.pButton = QtGui.QPushButton('Select question paper')
        self.pButton.clicked.connect(self.getPaper)
        self.details_page.registerField("PAPER", self.paper)
        self.MS = QtGui.QLineEdit()
        self.mButton = QtGui.QPushButton('Select mark scheme')
        self.mButton.clicked.connect(self.getMS)
        self.details_page.registerField("MS", self.MS)
        # -- Layout
        self.details_layout = QtGui.QGridLayout()
        self.details_layout.addWidget(self.details_instructions, 0, 0, 1, 2)
        self.details_layout.addWidget(self.details_nameLabel, 1, 0)
        self.details_layout.addWidget(self.details_nameLineEdit, 1, 1)
        self.details_layout.addWidget(self.courseLabel, 2, 0)
        self.details_layout.addWidget(self.coursebox, 2, 1)
        self.details_layout.addWidget(self.numlabel, 3, 0)
        self.details_layout.addWidget(self.numspin, 3, 1)
        self.details_layout.addWidget(self.pButton, 4, 0)
        self.details_layout.addWidget(self.paper, 4, 1)
        self.details_layout.addWidget(self.mButton, 5, 0)
        self.details_layout.addWidget(self.MS, 5, 1)
        self.details_page.setLayout(self.details_layout)

        ########################################################################

        # -- This page allows users to specify question level details
        # NOTE: the actual questions are added by the handle_next()
        # function based on user input on the details page.
        self.question_page = QtGui.QWizardPage()
        self.question_page.setTitle("Questions")
        self.question_label = QtGui.QLabel(
            "Please specify the title, module, topic "
            "and available marks for each question:")
        self.question_label.setWordWrap(True)
        # -- Scroll area widget contents
        self.question_scrollLayout = QtGui.QFormLayout()
        self.question_scrollWidget = QtGui.QWidget()
        self.question_scrollWidget.setLayout(self.question_scrollLayout)
        # -- Scroll area
        self.question_scrollArea = QtGui.QScrollArea()
        self.question_scrollArea.setWidgetResizable(True)
        self.question_scrollArea.setWidget(self.question_scrollWidget)
        # -- Layout
        self.question_body_layout = QtGui.QVBoxLayout()
        self.question_body_layout.addWidget(self.question_label)
        self.question_body_layout.addWidget(self.question_scrollArea)
        self.question_page.setLayout(self.question_body_layout)

        ########################################################################

        # -- Set grade Boundaries
        # NOTE: This needs an overhaul:
        # grades should be set through the course with the option
        # for Pass/Fail and admin style Complete/Pending
        self.boundary_page = QtGui.QWizardPage()
        self.boundary_page.setTitle("Grade Boundaries")
        self.boundary_label = QtGui.QLabel(
            "WARNING!!!\n\nAt present your grade boundaries MUST cover all "
            "available grades for this course: if you do not then grade "
            "based analysis will be disabled when you come to entering data.\n"
            "Innes will fix this in the future (I promise!)...\n\n"
            "Please specify available grades and percentage lower bounds:")
        self.boundary_label.setWordWrap(True)
        # -- Set up the grade boundary entry template
        self.boundaryBox = QtGui.QWidget()
        self.boundaryLayout = QtGui.QVBoxLayout()
        self.boundaryPageLayout = QtGui.QHBoxLayout()
        headings = QtGui.QWidget()
        hlayout = QtGui.QHBoxLayout()
        g = QtGui.QLabel(" Grade ")
        p = QtGui.QLabel("   %   ")
        hlayout.addWidget(g)
        hlayout.addWidget(p)
        headings.setLayout(hlayout)
        self.boundaryLayout.addWidget(headings)
        for b in range(12):
            pair = QtGui.QWidget()
            pairlayout = QtGui.QHBoxLayout()
            grade = QtGui.QLineEdit()
            perc = QtGui.QLineEdit()
            pairlayout.addWidget(grade)
            pairlayout.addWidget(perc)
            pair.setLayout(pairlayout)
            self.boundaryLayout.addWidget(pair)
        self.boundaryLayout.setSpacing(0)
        self.boundaryLayout.setContentsMargins(0, 0, 0, 0)
        self.boundaryBox.setLayout(self.boundaryLayout)
        self.boundaryPageLayout.addWidget(self.boundaryBox)
        self.boundaryPageLayout.addSpacing(400)
        self.bmain = QtGui.QWidget()
        self.bmain.setLayout(self.boundaryPageLayout)
        # -- Whole page layout including scrolling if needed
        self.boundary_scrollLayout = QtGui.QFormLayout()
        self.boundary_scrollWidget = QtGui.QWidget()
        self.boundary_scrollWidget.setLayout(self.boundary_scrollLayout)
        self.boundary_scrollArea = QtGui.QScrollArea()
        self.boundary_scrollArea.setWidgetResizable(True)
        self.boundary_scrollArea.setWidget(self.boundary_scrollWidget)
        self.boundary_scrollLayout.addWidget(self.bmain)
        self.blayout = QtGui.QVBoxLayout()
        self.blayout.addWidget(self.boundary_label)
        self.blayout.addWidget(self.boundary_scrollArea)
        self.boundary_page.setLayout(self.blayout)

        ########################################################################

        # -- Collate all user entered data and present it for confirmation
        self.confirm_page = QtGui.QWizardPage()
        self.confirm_page.setTitle("Confirm Assessment Entry")
        self.confirm_label = QtGui.QLabel(
            "Please check over all assessment details and confirm:")
        self.confirm_label.setWordWrap(True)
        self.course_title = QtGui.QLabel()
        self.assessment_title = QtGui.QLabel()
        self.paper_path = QtGui.QLabel()
        self.MS_path = QtGui.QLabel()
        self.boundary_list = QtGui.QLabel()
        # -- Whole page layout including scrolling if needed
        self.confirm_scrollLayout = QtGui.QFormLayout()
        self.confirm_scrollWidget = QtGui.QWidget()
        self.confirm_scrollWidget.setLayout(self.confirm_scrollLayout)
        # -- Scroll area
        self.confirm_scrollArea = QtGui.QScrollArea()
        self.confirm_scrollArea.setWidgetResizable(True)
        self.confirm_scrollArea.setWidget(self.confirm_scrollWidget)
        # -- Overall layout
        self.confirm_body_layout = QtGui.QVBoxLayout()
        self.confirm_body_layout.addWidget(self.confirm_label)
        self.confirm_body_layout.addWidget(self.course_title)
        self.confirm_body_layout.addWidget(self.assessment_title)
        self.confirm_body_layout.addWidget(self.paper_path)
        self.confirm_body_layout.addWidget(self.MS_path)
        self.confirm_body_layout.addWidget(self.boundary_list)
        self.confirm_body_layout.addWidget(self.confirm_scrollArea)
        self.confirm_page.setLayout(self.confirm_body_layout)

        ########################################################################

        # -- Report on success of saving to the database
        # This should warn the user if there was a problem!
        self.done_page = QtGui.QWizardPage()
        self.done_page.setTitle("Course Entry Complete")
        self.done_label = QtGui.QLabel(
            "Your course has now been stored in ClMATE. "
            "It may now be used to create assessments.")
        self.done_label.setWordWrap(True)
        self.done_layout = QtGui.QVBoxLayout()
        self.done_layout.addWidget(self.done_label)
        self.done_page.setLayout(self.done_layout)

        ########################################################################

        # -- Set up the page order of the wizard
        self.addPage(intro_page)
        self.addPage(self.details_page)
        self.addPage(self.question_page)
        self.addPage(self.boundary_page)
        self.addPage(self.confirm_page)
        self.addPage(self.done_page)
        self.setWizardStyle(self.ModernStyle)
        self.setWindowTitle(window_heading)
        self.setPixmap(0, QtGui.QPixmap('ClMATE/resources/watermark.png'))
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.handle_next)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.handle_assignment)

        self.resize(1150, 600)
        self.center()
        self.show()

    def handle_next(self):
        '''
        Utility method for processing user input as they
        progress through the setup wizard.
        '''
        # -- find the current page ID and handle accordingly
        id = self.currentId()
        # -- Question set up
        if id == 2:
            # -- If the user has previously had different questions remove them
            self.course = str(self.details_page.field("COURSE"))
            if self.question_scrollLayout.count():
                for row in range(self.question_scrollLayout.count()):
                    p = self.question_scrollLayout.itemAt(0).widget()
                    p.deleteLater()
                    self.question_scrollLayout.removeWidget(p)
            # -- Set up the correct number of question widgets
            numQs = int(self.details_page.field("NUMQs"))
            for q in range(numQs):
                question = Question(self, q + 1)
                self.question_scrollLayout.addWidget(question)
        # -- Boundary set up
        elif id == 4:
            # -- Rip boundary information from the boundary page
            self.aBoundaries = []
            aName = str(self.details_page.field("ASSESSMENT_NAME"))
            for row in range(12):
                # This is the container for the boundary information
                b_box = self.boundaryLayout.itemAt(row + 1).widget().layout()
                grade = str(b_box.itemAt(0).widget().text())
                perc = str(b_box.itemAt(1).widget().text())
                if grade:
                    if perc:
                        perc = int(perc)
                        self.aBoundaries.append((self.aID, aName, grade, perc))
                    else:
                        QtGui.QMessageBox.question(
                            self,
                            'Warning',
                            "You specified a grade but no percentage lower bound.")
            # -- Test for the existance of a 0
            if self.aBoundaries:
                if self.aBoundaries[-1][3] != 0:
                    self.aBoundaries.append((aName, 'Fail', 0))
                    QtGui.QMessageBox.question(
                        self,
                        'Warning',
                        "You did not specify a 0 mark lower bound. \n"
                        "(Fail: 0%) Has been added to your grade "
                        "boundaries.\n To remove this please specify a "
                        "catch-all grade below your current lowest grade.")
                # -- Format boundary information for the summary page
                nice_boundaries = ''
                for b in self.aBoundaries:
                    nice_boundaries = (nice_boundaries +
                                       str(b[2]) +
                                       ': ' +
                                       str(b[3]) +
                                       '%   ')
                self.aBoundaries = tuple(self.aBoundaries)
            # -- Warn that no boundaries were entered
            else:
                QtGui.QMessageBox.question(
                    self,
                    'Warning',
                    "You did not specify any grade boundaries."
                    "\nA default X grade has been entered."
                    "\nAnalysis against pupil targets will be "
                    "unavailable with this assessment.")
                nice_boundaries = ''
                nice_boundaries = "X: 0%"
                self.aBoundaries = (aName, 'X', 0)
            # -- Locate the remaining information required for the summary page
            course = str(self.details_page.field("COURSE"))
            self.course_title.setText("    Course Title:   " + course)
            self.assessment_title.setText("    Assessment Title:   " + aName)
            paper = str(self.details_page.field("PAPER"))
            self.paper_path.setText("    Question Paper:   " + paper)
            MS = str(self.details_page.field("MS"))
            self.MS_path.setText("    Mark Scheme:   " + MS)
            self.boundary_list.setText("    Grade Boundaries:   " +
                                       str(nice_boundaries))
            # -- Clear the current question layout if needed
            if self.confirm_scrollLayout.count():
                for row in range(self.confirm_scrollLayout.count()):
                    p = self.confirm_scrollLayout.itemAt(0).widget()
                    p.deleteLater()
                    self.confirm_scrollLayout.removeWidget(p)
            # -- Populate the question layout
            numQs = int(self.details_page.field("NUMQs"))
            self.questions = []
            # -- Element headings
            summary = QtGui.QWidget()
            summary_layout = QtGui.QHBoxLayout()
            summary_layout.addWidget(QtGui.QLabel("#"))
            summary_layout.addWidget(QtGui.QLabel("Question"))
            summary_layout.addWidget(QtGui.QLabel("Module"))
            summary_layout.addWidget(QtGui.QLabel("Topic"))
            summary_layout.addWidget(QtGui.QLabel("Marks"))
            summary.setLayout(summary_layout)
            self.confirm_scrollLayout.addWidget(summary)
            # -- Aquire question details and populate the question layout
            DBname = self.session_details["DBname"]
            with sqlite3.connect(DBname) as DB:
                ID_query = "select course_ID from courses where course_title = ?"
                course_ID = int(DB.execute(ID_query, (course,)).fetchone()[0])
                for row in range(numQs):
                    # -- Rip values from Question widgets
                    q = self.question_scrollLayout.itemAt(row).widget()
                    num = row + 1
                    numl = QtGui.QLabel(str(num))
                    title = str(q.qbox.text())
                    titlel = QtGui.QLabel(title)
                    module = str(q.qmodule.currentText())
                    modulel = QtGui.QLabel(module)
                    ID_query = "select module_ID from modules where module = ?"
                    module_ID = int(DB.execute(ID_query, (module,)).fetchone()[0])
                    topic = str(q.qtopic.currentText())
                    topicl = QtGui.QLabel(topic)
                    marks = q.qmarks.value()
                    marksl = QtGui.QLabel('/' + str(marks))
                    self.questions.append((self.aID,
                                           aName,
                                           course,
                                           course_ID,
                                           num,
                                           title,
                                           module,
                                           module_ID,
                                           topic,
                                           marks))
                    # Set up question summary and insert into the question layout
                    summary = QtGui.QWidget()
                    summary_layout = QtGui.QHBoxLayout()
                    summary_layout.addWidget(numl)
                    summary_layout.addWidget(titlel)
                    summary_layout.addWidget(modulel)
                    summary_layout.addWidget(topicl)
                    summary_layout.addWidget(marksl)
                    summary.setLayout(summary_layout)
                    self.confirm_scrollLayout.addWidget(summary)
            DB.close()

            # -- Store question details as a tuple for saveing to the database
            self.questions = tuple(self.questions)

        # -- Save the assessment data to the database
        elif id == 5:
            aName = str(self.details_page.field("ASSESSMENT_NAME"))
            paper = str(self.details_page.field("PAPER"))
            MS = str(self.details_page.field("MS"))

            DBname = self.session_details["DBname"]
            with sqlite3.connect(DBname) as DB:
                for Q in self.questions:
                    a_insert = ("insert into assessments (aID, aName, course, "
                                "course_ID, qNum, qTitle, qModule, module_ID, "
                                "qTopic, qMark) values (?,?,?,?,?,?,?,?,?,?)")
                    DB.execute(a_insert, Q)
                for g in self.aBoundaries:
                    g_insert = ("insert into gradeBoundaries "
                                "(aID, aName, grade, perc) values (?,?,?,?)")
                    DB.execute(g_insert, g)
                aDoc_insert = ("insert into assessmentDocs "
                               "(aID, aName, paper, MS) values(?,?,?,?)")
                DB.execute(aDoc_insert, (self.aID, aName, paper, MS))
            DB.close()

    def handle_assignment(self):
        '''
        Utility method for assigning an assessment
        to classes once creation is complete.
        '''
        global assigner
        course = str(self.details_page.field("COURSE"))
        aName = str(self.details_page.field("ASSESSMENT_NAME"))
        assigner = GroupSelectionWindow(self.aID, aName, course)

    def fileSelect(self):
        '''
        Utility method for locating a file path.
        '''
        # This defaults to the user's home directory
        filename = QtGui.QFileDialog.getOpenFileName(
            self,
            'Please select a file to attach',
            os.path.expanduser("~"))
        if sys.platform == 'win32':
            path_list = filename.split('/')
            filename = '\\'.join(path_list)
        return filename

    def getPaper(self):
        '''
        Wrapper for fileSelect().
        '''
        paper = self.fileSelect()
        self.paper.setText(paper)

    def getMS(self):
        '''
        Wrapper for fileSelect().
        '''
        MS = self.fileSelect()
        self.MS.setText(MS)

    def center(self):
        '''
        Locate screen dimensions and centre the widget accordingly.
        '''
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)         # boo for American spellings
        self.move(qr.topLeft())


class Question(QtGui.QWidget):
    '''
    NOTE:: These options populate based on user entered
    courses and topics via the course manager.
    '''
    def __init__(self, newAssm, qnum):
        super(Question, self).__init__()
        self.qnum = qnum
        COURSE = newAssm.course
        # -- Define fields for the question widget
        self.qnum = QtGui.QLabel(str(qnum), self)
        self.qbox = QtGui.QLineEdit()
        self.qbox.setPlaceholderText("{Question title}")
        self.qmodule = QtGui.QComboBox()

        # -- Locate availible modules in the database
        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            query = "select module from courses where course_title = ?"
            MODULES = DB.execute(query, (COURSE,)).fetchall()
        DB.close()

        for m in MODULES:
            self.qmodule.addItem(str(m[0]))
        self.qtopic = QtGui.QComboBox()
        self.qmodule.currentIndexChanged.connect(self.update_module)
        self.update_module()
        self.qmarks = QtGui.QSpinBox()
        self.qmarks.setMinimum(1)
        # -- Assemble the Question widget
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.qnum)
        layout.addWidget(self.qbox)
        layout.addWidget(self.qmodule)
        layout.addWidget(self.qtopic)
        layout.addWidget(self.qmarks)
        self.setLayout(layout)

    def update_module(self):
        '''
        Re-populates the topic comboBox when the module
        is changed for a question.
        '''
        MODULE = str(self.qmodule.currentText())
        self.qtopic.clear()
        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            t_query = "select topic from modules where module = ?"
            TOPICS = DB.execute(t_query, (MODULE,)).fetchall()
        DB.close()

        for t in TOPICS:
            self.qtopic.addItem(str(t[0]))


class AssessmentAssigner(StdWindow):
    '''
    A simple window that displays the current classes on the course
    specified at assessment creation and allows the user to select
    which classes to assign the assessment to.
    '''
    def __init__(self, session_details):
        super(AssessmentAssigner, self).__init__()
        self.session_details = session_details
        self.initUI(session_details)
        self.show()
        global numRows, COURSE
        numRows = 0
        COURSE = None

    def initUI(self, session_details):
        self.resize(800, 400)
        # main buttons
        self.yrGroup = QtGui.QComboBox()

        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            query = "select distinct course_ID from courses"
            COURSE_IDs = DB.execute(query).fetchall()
            for c in COURSE_IDs:
                c_query = "select course_title from courses where course_ID = ?"
                course = DB.execute(c_query, (int(c[0]),)).fetchall()[0][0]
                self.yrGroup.addItem(str(course),)
        DB.close()

        self.aName = QtGui.QComboBox()

        self.yrGroup.currentIndexChanged.connect(self.update_course)
        self.update_course()

        self.viewButton = QtGui.QPushButton('View Assessment')
        self.viewButton.clicked.connect(self.display_assessment)

        self.selectButton = QtGui.QPushButton('Assign')
        self.selectButton.clicked.connect(self.assign_to_groups)

        # scroll area widget contents - layout
        self.scrollLayout = QtGui.QFormLayout()
        # scroll area widget contents
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        # scroll area
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        # main layout
        self.mainLayout = QtGui.QVBoxLayout()
        # button layout
        self.buttonWidget = QtGui.QWidget()
        self.buttonArea = QtGui.QHBoxLayout()
        self.buttonArea.addWidget(self.yrGroup)
        self.buttonArea.addWidget(self.aName)
        self.buttonArea.addWidget(self.viewButton)
        self.buttonArea.addWidget(self.selectButton)

        self.buttonWidget.setLayout(self.buttonArea)
        # add all main to the main vLayout
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addWidget(self.scrollArea)
        self.setLayout(self.mainLayout)

        super(AssessmentAssigner, self).initUI()
        self.setWindowTitle("Assign Assessments")

    def update_course(self):
        '''
        Re-populates the assessment comboBox when the course
        selection is changed.
        '''
        global COURSE
        COURSE = str(self.yrGroup.currentText())
        self.aName.clear()

        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            query = "select distinct aID from assessments where course = ?"
            aIDs = DB.execute(query, (COURSE,)).fetchall()
            self.name_ID_pairs = []
            for a in aIDs:
                ID = int(a[0])
                aID_query = "select aName from assessments where aID = ?"
                aName = DB.execute(aID_query, (ID,)).fetchone()[0]
                self.aName.addItem(str(aName))
                self.name_ID_pairs.append((str(aName), ID))
        DB.close()
        self.name_ID_pairs = dict(self.name_ID_pairs)

    def display_assessment(self):
        '''
        This pulls results from the database and formats them for viewing.
        '''
        if self.scrollLayout.count():
            for row in range(self.scrollLayout.count()):
                p = self.scrollLayout.itemAt(0).widget()
                p.deleteLater()
                self.scrollLayout.removeWidget(p)

        summary = QtGui.QWidget()
        summary_layout = QtGui.QHBoxLayout()
        summary_layout.addWidget(QtGui.QLabel("#"))
        summary_layout.addWidget(QtGui.QLabel("Question"))
        summary_layout.addWidget(QtGui.QLabel("Module"))
        summary_layout.addWidget(QtGui.QLabel("Topic"))
        summary_layout.addWidget(QtGui.QLabel("Marks"))
        summary.setLayout(summary_layout)
        self.scrollLayout.addWidget(summary)

        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            query = "select * from assessments where aName = ?"
            aName = str(self.aName.currentText())
            questions = DB.execute(query, (aName,)).fetchall()
        DB.close()

        for row in range(len(questions)):
            # Display question details
            num = row + 1
            numl = QtGui.QLabel(str(num))
            title = str(questions[row][3])
            titlel = QtGui.QLabel(title)
            module = str(questions[row][4])
            modulel = QtGui.QLabel(module)
            topic = str(questions[row][5])
            topicl = QtGui.QLabel(topic)
            marks = str(questions[row][6])
            marksl = QtGui.QLabel('/' + str(marks))
            # Set up summary screen
            summary = QtGui.QWidget()
            summary_layout = QtGui.QHBoxLayout()
            summary_layout.addWidget(numl)
            summary_layout.addWidget(titlel)
            summary_layout.addWidget(modulel)
            summary_layout.addWidget(topicl)
            summary_layout.addWidget(marksl)
            summary.setLayout(summary_layout)
            self.scrollLayout.addWidget(summary)

    def remove_question(self):
        '''
        Delete the last Question widget in the current layout.
        '''
        global numRows
        lastRow = numRows - 1
        q = self.scrollLayout.itemAt(lastRow).widget()
        q.deleteLater()
        numRows -= 1

    def assign_to_groups(self):
        '''
        Open the GroupSelectionWindow and close the AssessmentAssigner window.
        '''
        global assignment_window
        aID = self.name_ID_pairs[str(self.aName.currentText())]
        assignment_window = GroupSelectionWindow(
            self.session_details,
            aID,
            str(self.aName.currentText()),
            str(self.yrGroup.currentText()))
        self.close()


class GroupSelectionWindow(StdWindow):
    '''
    View available groups and select which ones you would
    like to assign the chosen assessment to.
    '''
    def __init__(self, session_details, aID, chosenAssessment, year):
        self.aID = aID
        self.chosen = chosenAssessment
        self.yearGroup = year
        super(GroupSelectionWindow, self).__init__()
        self.initUI()
        self.show()

    def initUI(self):
        self.commitButton = QtGui.QPushButton('Assign')
        self.commitButton.clicked.connect(self.commit_to_DB)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.group_getter(), 0, 0)
        grid.addWidget(self.commitButton, 1, 1)
        self.setLayout(grid)
        super(GroupSelectionWindow, self).initUI()
        self.setWindowTitle(self.chosen)

    def group_getter(self):
        '''
        A grid of available groups.
        '''
        self.groupBox = QtGui.QGroupBox('Select Groups')
        self.bGroup = QtGui.QVBoxLayout()

        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            query = "select distinct teaching_set from staffing where course = ?"
            validGroups = DB.execute(query, (self.yearGroup,)).fetchall()
        DB.close()

        for g in validGroups:
            check = QtGui.QCheckBox(g[0])
            self.bGroup.addWidget(check)
        self.groupBox.setLayout(self.bGroup)
        return self.groupBox

    def commit_to_DB(self):
        assignTest = ("insert into assignedTests (aID, aName, teaching_set)"
                      " values (?, ?, ?)")

        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            chosenGroups = list()
            for b in range(self.bGroup.count()):
                g = self.bGroup.itemAt(b).widget()
                # look if box is checked and if so add that group to the list
                if g.checkState():
                    query = ("select 1 from assignedTests where aID = ? "
                             "and teaching_set = ?")
                    if DB.execute(query, (self.aID, str(g.text()))).fetchone():
                        pass
                    else:
                        chosenGroups.append(str(g.text()))
            for c in chosenGroups:
                assignment = (self.aID, self.chosen, c)
                DB.execute(assignTest, assignment)
        DB.close()
        self.close()


class AssessmentDeleter(StdWindow):
    def __init__(self):
        super(AssessmentDeleter, self).__init__()
        self.initUI()
        self.show()

    def initUI(self):
        super(AssessmentDeleter, self).initUI()
        self.setWindowTitle("Delete Assessments")


class Course(QtGui.QWizard):
    def __init__(self, session_details):
        super(Course, self).__init__()
        icon = QtGui.QIcon('ClMATE/resources/logo.png')
        self.setWindowIcon(icon)

        intro_page = QtGui.QWizardPage()
        intro_page.setTitle("ClMATE Course Creator")
        intro_label = QtGui.QLabel(
            "Welcome to the ClMATE course creator tool."
            "\n\nBefore you begin, make sure that you have "
            "all module and topic details at hand.")
        intro_label.setWordWrap(True)
        intro_layout = QtGui.QVBoxLayout()
        intro_layout.addWidget(intro_label)
        intro_page.setLayout(intro_layout)

        ###############################################

        self.module_page = QtGui.QWizardPage()
        self.module_page.setTitle("Course Title and Modules")

        self.module_instructions = QtGui.QLabel(
            "Please specify the name of the course and "
            "all modules to be studied separated by semi-colons:")

        self.module_nameLabel = QtGui.QLabel("Course Name:")
        self.module_nameLineEdit = QtGui.QLineEdit()
        self.module_page.registerField("COURSE_NAME*", self.module_nameLineEdit)

        self.moduleLabel = QtGui.QLabel("Modules:")
        self.moduleLineEdit = QtGui.QLineEdit()
        # The * postfix denotes this as a required field before continuing.
        self.module_page.registerField("MODULES*", self.moduleLineEdit)

        self.module_layout = QtGui.QGridLayout()
        self.module_layout.addWidget(self.module_instructions, 0, 0, 1, 3)
        self.module_layout.addWidget(self.module_nameLabel, 1, 0)
        self.module_layout.addWidget(self.module_nameLineEdit, 1, 1)
        self.module_layout.addWidget(self.moduleLabel, 2, 0)
        self.module_layout.addWidget(self.moduleLineEdit, 2, 1)
        self.module_page.setLayout(self.module_layout)

        ###############################################

        self.topic_page = QtGui.QWizardPage()
        self.topic_page.setTitle("Module Topics")
        self.topic_label = QtGui.QLabel(
            "Please specify the topics within each module that "
            "you would like to track separated by semi-colons:")
        self.topic_label.setWordWrap(True)

        # scroll area widget contents
        self.topic_scrollLayout = QtGui.QFormLayout()
        self.topic_scrollWidget = QtGui.QWidget()
        self.topic_scrollWidget.setLayout(self.topic_scrollLayout)
        # scroll area
        self.topic_scrollArea = QtGui.QScrollArea()
        self.topic_scrollArea.setWidgetResizable(True)
        self.topic_scrollArea.setWidget(self.topic_scrollWidget)

        self.topic_body_layout = QtGui.QVBoxLayout()
        self.topic_body_layout.addWidget(self.topic_label)
        self.topic_body_layout.addWidget(self.topic_scrollArea)

        self.topic_page.setLayout(self.topic_body_layout)

        ###############################################

        self.confirm_page = QtGui.QWizardPage()
        self.confirm_page.setTitle("Confirm Course Entry")
        self.confirm_label = QtGui.QLabel(
            "Please check over all course details and confirm:")
        self.confirm_label.setWordWrap(True)

        self.course_title = QtGui.QLabel()

        # scroll area widget contents
        self.confirm_scrollLayout = QtGui.QFormLayout()
        self.confirm_scrollWidget = QtGui.QWidget()
        self.confirm_scrollWidget.setLayout(self.confirm_scrollLayout)
        # scroll area
        self.confirm_scrollArea = QtGui.QScrollArea()
        self.confirm_scrollArea.setWidgetResizable(True)
        self.confirm_scrollArea.setWidget(self.confirm_scrollWidget)

        self.confirm_body_layout = QtGui.QVBoxLayout()
        self.confirm_body_layout.addWidget(self.confirm_label)
        self.confirm_body_layout.addWidget(self.course_title)
        self.confirm_body_layout.addWidget(self.confirm_scrollArea)

        self.confirm_page.setLayout(self.confirm_body_layout)

        ###############################################

        self.done_page = QtGui.QWizardPage()
        self.done_page.setTitle("Course Entry Complete")
        self.done_label = QtGui.QLabel(
            "Your course has now been stored in ClMATE. "
            "It may now be used to create assessments.")
        self.done_label.setWordWrap(True)

        self.done_layout = QtGui.QVBoxLayout()
        self.done_layout.addWidget(self.done_label)
        self.done_page.setLayout(self.done_layout)

        ###############################################

        self.addPage(intro_page)
        self.addPage(self.module_page)
        self.addPage(self.topic_page)
        self.addPage(self.confirm_page)
        self.addPage(self.done_page)
        self.setWizardStyle(self.ModernStyle)
        self.setWindowTitle(window_heading)
        self.setPixmap(0, QtGui.QPixmap('ClMATE/resources/watermark.png'))
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.handle_next)
        self.show()

    def handle_next(self):
        id = self.currentId()
        if id == 2:
            self.course_name = str(self.module_page.field("COURSE_NAME"))
            self.modules = str(self.module_page.field("MODULES")).split('; ')
            if self.topic_scrollLayout.count():
                for row in range(self.topic_scrollLayout.count()):
                    p = self.topic_scrollLayout.itemAt(0).widget()
                    p.deleteLater()
                    self.topic_scrollLayout.removeWidget(p)
            if self.modules != ['']:
                for m in enumerate(self.modules):
                    modlabel = QtGui.QLabel(m[1])
                    topic_box = QtGui.QLineEdit()
                    self.module_page.registerField(m[1], topic_box)
                    pair = QtGui.QWidget()
                    pair_layout = QtGui.QHBoxLayout()
                    pair_layout.addWidget(modlabel)
                    pair_layout.addWidget(topic_box)
                    pair.setLayout(pair_layout)
                    self.topic_scrollLayout.addWidget(pair)

        elif id == 3:
            self.course_title.setText(
                "Course Title: " +
                str(self.module_page.field("COURSE_NAME")))
            if self.confirm_scrollLayout.count():
                for row in range(self.confirm_scrollLayout.count()):
                    p = self.confirm_scrollLayout.itemAt(0).widget()
                    p.deleteLater()
                    self.confirm_scrollLayout.removeWidget(p)
            for m in enumerate(self.modules):
                topics = str(self.topic_page.field(m[1]))
                split_topics = str(self.topic_page.field(m[1])).split('; ')
                modlabel = QtGui.QLabel(m[1])
                topiclabel = QtGui.QLabel(topics)
                topiclabel.setWordWrap(True)
                pair = QtGui.QWidget()
                pair_layout = QtGui.QHBoxLayout()
                pair_layout.addWidget(modlabel)
                pair_layout.addWidget(topiclabel)
                pair.setLayout(pair_layout)
                self.confirm_scrollLayout.addWidget(pair)

        elif id == 4:
            # save data to the database
            DBname = self.session_details["DBname"]
            with sqlite3.connect(DBname) as DB:
                ID_query = ("select course_ID from courses "
                            "order by course_ID desc limit 1")
                course_ID = DB.execute(ID_query).fetchone()
                if course_ID:
                    course_ID = int(course_ID[0]) + 1
                else:
                    course_ID = 1
                addmodule = ("insert into courses (course_title, "
                             "course_ID, module) values (?,?,?)")
                addtopic = ("insert into modules (module, module_ID, "
                            "topic) values (?,?,?)")
                module_list = []
                topic_list = []
                for m in enumerate(self.modules):
                    module_list.append((self.course_name, course_ID, m[1]))
                    query = ("select module_ID from modules "
                             "order by module_ID desc limit 1")
                    module_ID_current_max = DB.execute(query).fetchone()
                    if module_ID_current_max:
                        module_ID = int(module_ID_current_max[0]) + 1 + m[0]
                    else:
                        module_ID = 1 + m[0]
                    split_topics = str(self.topic_page.field(m[1])).split('; ')
                    for t in split_topics:
                        topic_list.append((m[1], module_ID, t))
                for module in module_list:
                    DB.execute(addmodule, module)
                for topic in topic_list:
                    DB.execute(addtopic, topic)
            DB.close()


class CourseEditor(StdWindow):
    def __init__(self):
        super(CourseEditor, self).__init__()
        self.initUI()
        self.show()

    def initUI(self):
        super(CourseEditor, self).initUI()
        self.setWindowTitle("Edit Course Details")


class CourseDeleter(StdWindow):
    def __init__(self):
        super(CourseDeleter, self).__init__()
        self.initUI()
        self.show()

    def initUI(self):
        super(CourseDeleter, self).initUI()
        self.setWindowTitle("Delete Courses")
