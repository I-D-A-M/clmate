from PyQt4 import QtGui, QtCore
from .definitions import grey, white, black, DBname
import sqlite3

def median(LIST):
    '''
    A simple helper function to calculate the median value of a list
    of numerical values.
    '''
    half = len(LIST) // 2
    LIST.sort()
    if len(LIST) % 2 == 0:
        return (LIST[half - 1] + LIST[half]) // 2
    else:
        return LIST[half]


def mean(LIST):
    '''
    A simple helper function to calculate the mean value of a list of
    numerical values formatted to two decimal places.
    '''
    mean = float("{0:.1f}".format(sum(LIST) / float(len(LIST))))
    return mean


def percentage_marks(p,q):
    return float("{0:.2f}".format((p/q)*100))


def colourise(pob):
    '''Assign each module / topic a colour based on the
       user defined colour scheme. '''
    # Will eventually need some way of storing and retrieving these
    # parameters in/from the databse via a config file.
    G=90.00
    O=60.00
    if pob >= G:
        colour = 'Green'
    elif pob >= O:
        colour = 'Orange'
    else:
        colour = 'Red'
    return colour


def createDB():
    '''
    This function creates the SQLite database required for CLMATE
    to function. It sets up all of the tables in addition to
    specifying default admin level access details.
    '''
    DB = sqlite3.connect(DBname)
    with DB:
        DB.execute("create table if not exists cohort (UPN text, Name text, "
                   "teaching_set text, SEN text, PP text, KS2Band text, "
                   "KS2lvl text, FFT text, GCSE_result text, ASAlps text, "
                   "ASResult text, A2Alps text)")
        DB.execute("create table if not exists courses (course_ID integer, "
                   "course_title text, module text)")
        DB.execute("create table if not exists modules (module_ID integer, "
                   "module text, topic text)")
        # Account types are teacher and admin:
        # -- Teachers only have access to information on their classes and are
        #    unable to create assessments or run full cohort analysis.
        #    Admin users have full control of the database and access to all
        #    analysis functionality.
        DB.execute("create table if not exists staff (staff_code text, "
                   "username text, password text, account_type text)")
        DB.execute("create table if not exists staffing (teaching_set text, "
                   "staff_code text, yrGroup text, course text)")
        DB.execute("create table if not exists assessments (aID integer, "
                   "aName text, course text, course_ID integer, qNum integer, "
                   "qTitle text, qModule text, module_ID integer, qTopic text, "
                   "qMark integer)")
        DB.execute("create table if not exists assignedTests (aID integer, "
                   "aName text, teaching_set text)")
        DB.execute("create table if not exists resits (parent_ID integer, "
                   "resit_ID, best_attempt text)")
        DB.execute("create table if not exists results (aID integer, UPN text, "
                   "teaching_set text, aName text, qNum integer, pMark integer)")
        DB.execute("create table if not exists assessmentDocs (aID integer, "
                   "aName text, paper text, MS text)")
        DB.execute("create table if not exists gradeBoundaries (aID integer, "
                   "aName text, grade text, perc integer)")
        DB.execute("create table if not exists pupilNotes (UPN text, note text)")
        # -- set up SQLite command templates
        addPupil = ("insert into cohort (UPN, Name, teaching_set, SEN, PP, "
                    "KS2Band, KS2lvl, FFT, GCSE_result, ASAlps, ASResult, A2Alps) "
                   "values (?,?,?,?,?,?,?,?,?,?,?,?)")
        addStaff = ("insert into staff (staff_code, username, password, "
                   "account_type) values (?, ?, ?, ?)")
        addStaffing = ("insert into staffing (teaching_set, staff_code, yrGroup, "
                      "course) values (?, ?, ?, ?)")
        # Will need an input window that looks at the available classes and
        # then sets up staffing based on this.
        # -- At present, the 'super' user will load ALL available
        #    classes when used as a login
        testStaff = (('SU', 'super', 'sudoaccess', 'admin'),
                     ('IM', 'morrisoni', 'z', 'admin'),
                     ('CS', 'stephensonc', 'passwd', 'admin'),
                     ('HH', 'hughesh', 'passwd', 'teacher'),
                     ('AK', 'kela', 'passwd', 'teacher'),
                     ('JB', 'brooksj', 'passwd', 'teacher'),
                     ('PK', 'kellyp', 'passwd', 'teacher'),
                     ('CCL', 'clarkec', 'passwd', 'teacher'),
                     ('PG', 'gatenbyp', 'passwd', 'teacher'),
                     ('AR', 'rosiea', 'passwd', 'teacher'),
                     ('AWH', 'wheelera', 'passwd', 'teacher'),
                     ('DBY', 'bodeyd', 'passwd', 'teacher'))
        # STAFFING WILL NEED TO BE ASSIGNABLE!!!
        testStaffing = (('11-IM 14/15', 'IM', 'GCSE', 'GCSE Higher'),
                        ('11-CS 14/15', 'CS', 'GCSE', 'GCSE Higher'),
                        ('11-HH 14/15', 'HH', 'GCSE', 'GCSE Higher'),
                        ('11-DBY 14/15', 'DBY', 'GCSE', 'GCSE Higher'),
                        ('11-AK 14/15', 'AK', 'GCSE', 'GCSE Higher'),
                        ('11-PG 14/15', 'PG', 'GCSE', 'GCSE Higher'),
                        ('11-PK 14/15', 'PK', 'GCSE', 'GCSE Higher'),
                        ('11-AR 14/15', 'AR', 'GCSE', 'GCSE Foundation'),
                        ('11-JB 14/15', 'JB', 'GCSE', 'GCSE Foundation'),
                        ('12D/Ma1 14/15', 'IM', 'AS', 'AS Core'),
                        ('12D/Ma1 14/15', 'JB', 'AS', 'AS Core'),
                        ('12D/Ma2 14/15', 'JB', 'AS', 'AS Core'),
                        ('12D/Ma2 14/15', 'PK', 'AS', 'AS Core'),
                        ('12C/Ma1 14/15', 'CS', 'AS', 'AS Core'),
                        ('12C/Ma1 14/15', 'CCL', 'AS', 'AS Core'),
                        ('12C/Ma2 14/15', 'AK', 'AS', 'AS Core'),
                        ('12C/Ma2 14/15', 'PG', 'AS', 'AS Core'))
        # -- Import default users and staffing to the database
        for staffmember in testStaff:
            DB.execute(addStaff, staffmember)
        for tset in testStaffing:
            DB.execute(addStaffing, tset)

    # This function needs to be pulled out to be a stand alone import
    # function that can be used to import large amounts of data to a
    # variety of locations.
    sheet_list = ["y11maths.xlsx", "y12maths.xlsx", "y13maths.xlsx"]
    for s in sheet_list:
        # -- Load each workbook as an iterator based openpyxl object
        #    and select the first sheet of each for copying.
        workbook = load_workbook(s, use_iterators=True)
        sheet = workbook.active
        testCohortList = []
        first_row = True
        for row in sheet.iter_rows():
            # -- Skip the header fields in the worksheet
            if first_row:
                first_row = False
            else:
                currentPupil = []
                for cell in row:
                    currentPupil.append(cell.value)
                testCohortList.append(tuple(currentPupil))
        testCohort = tuple(testCohortList)
        # -- Import pupil data into the database
        with DB:
            for pupil in testCohort:
                DB.execute(addPupil, pupil)
    DB.close()


def class_view(class_name, session_details):
    '''
    Read in class details from the database and display them in a read only
    format with the ability for users to store notes on class members.
    '''
    DBname = session_details["DBname"]
    DB = sqlite3.connect(DBname)
    class_name = str(class_name[0])
    # -- Locate pupil names and store as a list of strings [Name format will
    #    depend on the output from SIMS.net]
    NAMES = DB.execute("select name from cohort where teaching_set = ?",
                       (class_name,)).fetchall()
    name_list = []
    for p in range(len(NAMES)):
        n = str(NAMES[p][0])
        name_list.append(n)
    # Hard coded at present but ideally this should be a function that can
    # be set by the user when they set up a class / course
    yrGroup = DB.execute("select yrGroup from staffing where teaching_set = ?",
                         (class_name,)).fetchone()[0]
    if yrGroup == 'GCSE':
        TARGETS = DB.execute("select FFT from cohort where teaching_set = ?",
                             (class_name,)).fetchall()
        targetName = 'FFT'

    elif yrGroup == 'AS':
        TARGETS = DB.execute("select ASAlps from cohort where teaching_set = ?",
                             (class_name,)).fetchall()
        targetName = 'ALPs'
    elif yrGroup == 'A2':
        TARGETS = DB.execute("select A2Alps from cohort where teaching_set = ?",
                             (class_name,)).fetchall()
        targetName = 'ALPs'
    else:
        failure = QtGui.QMessageBox.question(self, 'Warning!',
                            "Unable to find year group for current class.")
        return -1
    # -- Locate target grades
    target_list = []
    for t in range(len(TARGETS)):
        g = str(TARGETS[t][0])
        if g == 'None':
            # -- Use hidden default 'N/A' grade if none is found
            target_list.append('N/A')
        else:
            target_list.append(g)
    # -- Overview has three columns: name, target, notes
    class_overview = QtGui.QTableWidget(len(name_list), 3)
    # -- Define which cells are editable, initial content and colourschemes
    for r in range(len(name_list)):
        namecell = QtGui.QTableWidgetItem()
        namecell.setBackgroundColor(grey)
        namecell.setFlags(QtCore.Qt.NoItemFlags)
        namecell.setText(name_list[r])
        namecell.setTextColor(white)
        class_overview.setItem(r, 0, namecell)

        targetcell = QtGui.QTableWidgetItem()
        targetcell.setBackgroundColor(grey)
        targetcell.setFlags(QtCore.Qt.NoItemFlags)
        targetcell.setText(target_list[r])
        targetcell.setTextColor(white)
        class_overview.setItem(r, 1, targetcell)
    # The notes column needs to be implemented!
    # -- Set column headers
    oHeader_list = ['Name', targetName, 'Notes [NOT CURRENTLY ACTIVE!]']
    class_overview.setHorizontalHeaderLabels(oHeader_list)
    class_overview.resizeColumnToContents(0)
    class_overview.setColumnWidth(1, 60)
    class_overview.setColumnWidth(2, 500)
    return class_overview
