from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from openpyxl import Workbook, load_workbook
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3

from .definitions import DEFAULT_PLOT_WIDTH, DEFAULT_PLOT_HEIGHT
from .definitions import DEFAULT_PLOT_DPI, plot_style
from .helpers import percentage_marks, colourise
from .main_interface import OverviewWidget


class Analyser(QtGui.QWidget):
    '''
    The main widget screen for displaying summaries and plots to the user.
    The views on the data will be shown in the 'mainArea' widget.
    '''
    def __init__(self, teaching_set, session_details):
        super(Analyser, self).__init__()
        self.session_details = session_details
        self.permissionLevel = self.session_details["permissionLevel"]
        self.DBname = self.session_details["DBname"]
        self.teaching_set = teaching_set
        self.title_string = 'Viewing data for ' + self.teaching_set
        self.coalation_type = 'mean'

        self.dataframe = self.get_data()
        # This will eventually be altered by the filters
        self.prepaired_dataframe = self.prepair_data(default=True,
                                                     tSet=self.teaching_set)

        self.grid = QtGui.QGridLayout()
        self.MainArea = self.mainArea()
        self.Filters = self.filters()
        self.Buttons = self.buttons()
        self.grid.addWidget(self.Filters, 0, 0, 1, 2)
        self.grid.addWidget(self.Buttons, 3, 0, 1, 2)
        self.grid.addWidget(self.MainArea, 0, 2, 4, 8)
        self.setLayout(self.grid)
        self.resize(1200, 600)

        self.update_plot()
        self.show()

    def get_data(self):
        DB = sqlite3.connect(self.DBname)
        if self.permissionLevel == 'admin':
            results = pd.read_sql("SELECT * from results", DB)
        else:
            ID_query = "SELECT staff_code from staff where username = ?"
            staffID = pd.read_sql(ID_query,
                                  DB,
                                  params=[username])
            set_query = "SELECT teaching_set from staffing where staff_code = ?"
            setlist = pd.read_sql(set_query,
                                  DB,
                                  params=[staffID['staff_code'][0]])
            sets = setlist['teaching_set'].tolist()
            results_query = (
                "SELECT * from results where "
                " or ".join(("teaching_set = " + "'"+str(n)+"'" for n in sets)))
            results = pd.read_sql(results_query, DB)
        assessments = pd.read_sql("SELECT * from assessments", DB)
        merged = pd.merge(
                        results,
                        assessments,
                        how='left',
                        left_on=['aID', 'qNum'],
                        right_on=['aID', 'qNum'])
        merged = merged.drop(
                        ['aName_y', 'qTitle',
                        'aName_x', 'course',
                        'course_ID', 'module_ID'],
                        axis=1)
        cols = ['aID', 'qNum', 'UPN', 'qModule', 'qTopic',
                'pMark', 'qMark', 'teaching_set']
        df = merged[cols]

        return df

    def prepair_data(self,
                     default=False,
                     analysis='Class-Cohort',
                     tSet='',
                     group_fields=['qModule']):
        '''
        This is - at present - a predefined if statement covering
        the different types of plot that the user can request.
        '''
        if group_fields == ['Error!']:
            warning = QtGui.QMessageBox.question(self, 'Uh oh...',
                            ("Something went wrong. "
                            "Please close the analysis screen and try again."))
        elif default == True:
            class_sorted = self.class_results(tSet, group_fields)
            cohort_sorted = self.cohort_results(group_fields)
            new_dataframe = pd.merge(
                        class_sorted,
                        cohort_sorted,
                        left_index=True,
                        right_index=True)
            new_dataframe.rename(
                        columns={'pob':'Class_percentage'},
                        inplace=True)

            # Sort the dataframe to be in alphabetical order
            # by index [The field grouped by]
            new_dataframe.sort_index(axis=0, ascending=False, inplace=True)
            return new_dataframe

        if analysis == 'Class-Cohort':
            class_sorted = self.class_results(tSet, group_fields)
            cohort_sorted = self.cohort_results(group_fields)
            new_dataframe = pd.merge(
                        class_sorted,
                        cohort_sorted,
                        left_index=True,
                        right_index=True)
            new_dataframe.rename(
                        columns={'pob_x':'Class_percentage',
                                 'pob_y':'Cohort_percentage'},
                                  inplace=True)
        elif analysis == 'Class':
            new_dataframe = self.class_results(tSet, group_fields)
            new_dataframe.rename(columns={'pob':'Class_percentage'},
                                 inplace=True)
        elif analysis == 'Cohort':
            new_dataframe = self.cohort_results(group_fields)
            new_dataframe.rename(columns={'pob':'Cohort_percentage'},
                                 inplace=True)
        else:
            new_dataframe = self.dataframe

        # Sort the dataframe to be in alphabetical order by index
        new_dataframe.sort_index(axis=0, ascending=False, inplace=True)
        return new_dataframe

    def class_results(self, tSet, group_fields):
        filtered = self.dataframe[self.dataframe['teaching_set'].isin([tSet])]
        cols = ['qModule', 'qTopic', 'qMark', 'pMark']
        df = filtered[cols]
        df_grouped = df.groupby(group_fields)

        if self.coalation_type == 'best':
            df = df_grouped.max()
            df['pob'] = np.vectorize(percentage_marks)(df['pMark'], df['qMark'])
            df['Colour'] = np.vectorize(colourise)(df['pob'])
            df.rename(columns={'pob':'Class Max percentage'}, inplace=True)
            df = df.drop(['pMark', 'qMark'], axis=1)
            if group_fields == ['qTopic']:
                df = df.drop(['qModule'], axis=1)
            elif group_fields == ['qModule']:
                df = df.drop(['qTopic'], axis=1)
        elif self.coalation_type == 'mean':
            df = df_grouped.mean()
            df['pob'] = np.vectorize(percentage_marks)(df['pMark'], df['qMark'])
            # Round off ALL values in the dataframe to 2 decimal places
            # otherwise the mean function will give ridiculous accuracy!
            df = np.round(df, 2)
            df['Colour'] = np.vectorize(colourise)(df['pob'])
            df = df.drop(['pMark', 'qMark'], axis=1)
            df.rename(columns={'pob':'Class Mean percentage'}, inplace=True)
        else:
            warning = QtGui.QMessageBox.question(self, 'Uh oh...',
                            ("Something went wrong."
                            "Please close the analysis screen and try again."))
        return df


    def cohort_results(self, group_fields):
        df_grouped = self.dataframe.groupby(group_fields)

        if self.coalation_type == 'best':
            df = df_grouped.max()
            df['pob'] = np.vectorize(percentage_marks)(df['pMark'], df['qMark'])
            df = df.drop(['pMark', 'qMark',  'aID', 'qNum'], axis=1)
            df['Colour'] = np.vectorize(colourise)(df['pob'])
            df.rename(columns={'pob':'Cohort Max percentage'}, inplace=True)
            if group_fields == ['qTopic']:
                df = df.drop(['qModule'], axis=1)
            elif group_fields == ['qModule']:
                df = df.drop(['qTopic'], axis=1)
        elif self.coalation_type == 'mean':
            df = df_grouped.mean()
            df['pob'] = np.vectorize(percentage_marks)(df['pMark'], df['qMark'])
            df = df.drop(['pMark', 'qMark',  'aID', 'qNum'], axis=1)
            # round off ALL values in the dataframe to 2 decimal places
            df = np.round(df, 2)
            df['Colour'] = np.vectorize(colourise)(df['pob'])
            df.rename(columns={'pob':'Cohort Mean percentage'}, inplace=True)
        else:
            warning = QtGui.QMessageBox.question(self, 'Uh oh...',
                            ("Something went wrong."
                            "Please close the analysis screen and try again."))
        return df


    def filters(self):
        DB = sqlite3.connect(self.DBname)
        filtersDetails = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()

        # Selection box for the analysis level
        self.levelBox = QtGui.QComboBox()
        # Pupil analysis will have: 'Pupil', 'Pupil-Class', 'Pupil-Cohort'
        for l in ['Class', 'Cohort', 'Class-Cohort']:
            self.levelBox.addItem(l)
        self.levelBox.currentIndexChanged.connect(self.update_level)

        self.level_selection = QtGui.QComboBox()
        if self.permissionLevel == 'admin':
            query = ("select distinct teaching_set from results "
                     "order by teaching_set desc")
            CLASSES = DB.execute(query).fetchall()
            for t in CLASSES:
                self.level_selection.addItem(str(t[0]))
        else:
            staff_query = "SELECT staff_code from staff where username = ?"
            staffID = pd.read_sql(staff_query,
                                  DB,
                                  params=[username])
            set_query = "SELECT teaching_set from staffing where staff_code = ?"
            setlist = pd.read_sql(set_query,
                                  DB,
                                  params=[staffID['staff_code'][0]])
            setlist = setlist['teaching_set'].tolist()
            query = ("select distinct teaching_set from results "
                     "order by teaching_set desc")
            valid_sets = DB.execute(query).fetchall()
            sets_with_results = [str(s[0]) for s in valid_sets]
            useable_sets = [s for s in setlist if s in sets_with_results]
            useable_sets.sort()
            for s in useable_sets:
                self.level_selection.addItem(s)
        self.level_selection.currentIndexChanged.connect(self.update_plot)

        # Selection box for the analysis type
        self.groupByBox = QtGui.QComboBox()
        for s in ['Modules', 'Topics']:
            self.groupByBox.addItem(s)
        self.groupByBox.currentIndexChanged.connect(self.update_plot)

        # Data coalation options
        self.coalationBox = QtGui.QGroupBox("Select Coalation Type")
        self.coalationBox.setCheckable(True)
        self.coalationBox.setChecked(False)

        self.radio_mean = QtGui.QRadioButton("Mean Average")
        self.radio_best = QtGui.QRadioButton("Best Sitting")
        self.radio_mean.setChecked(True)
        self.radio_mean.toggled.connect(self.radio_mean_clicked)
        self.radio_best.toggled.connect(self.radio_best_clicked)

        self.checkBox = QtGui.QCheckBox("Sort by Performance")
        self.checkBox.setChecked(False)
        fbox = QtGui.QVBoxLayout()
        fbox.addWidget(self.radio_mean)
        fbox.addWidget(self.radio_best)
        fbox.addWidget(self.checkBox)
        fbox.addStretch(1)
        self.coalationBox.setLayout(fbox)

        vbox.addWidget(self.levelBox)
        vbox.addWidget(self.level_selection)
        vbox.addWidget(self.groupByBox)
        vbox.addWidget(self.coalationBox)
        filtersDetails.setLayout(vbox)

        return filtersDetails

    def radio_mean_clicked(self, enabled):
        if enabled:
            self.coalation_type = 'mean'
            self.update_plot()

    def radio_best_clicked(self, enabled):
        if enabled:
            self.coalation_type = 'best'
            self.update_plot()

    def buttons(self):
        buttonBox = QtGui.QGroupBox()

        exitButton = QtGui.QPushButton("&Exit")
        exitButton.clicked.connect(self.replace_main_widget)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(exitButton)
        buttonBox.setLayout(vbox)

        return buttonBox

    def mainArea(self):
        ''' The mainArea requires a method for switching tabs
            so it is a class of its own.'''
        main_area = AnalysisMainArea(self.prepaired_dataframe)

        return main_area

    def update_level(self):
        level = str(self.levelBox.currentText())
        self.level_selection.clear()
        DB = sqlite3.connect(self.DBname)

        if level == 'Class' or 'Class-Cohort':
            if self.permissionLevel == 'admin':
                query = ("select distinct teaching_set from results "
                         "order by teaching_set desc")
                CLASSES = DB.execute(query).fetchall()
                for t in CLASSES:
                    self.level_selection.addItem(str(t[0]))
            else:
                query = "SELECT staff_code from staff where username = ?"
                staffID = pd.read_sql(query,
                                      DB,
                                      params=[username])
                query = "SELECT teaching_set from staffing where staff_code = ?"
                setlist = pd.read_sql(query,
                                      DB,
                                      params=[staffID['staff_code'][0]])
                setlist = setlist['teaching_set'].tolist()
                query = ("select distinct teaching_set from results "
                         "order by teaching_set desc")
                valid_sets = DB.execute(query).fetchall()
                sets_with_results = [str(s[0]) for s in valid_sets]
                useable_sets = [s for s in setlist if s in sets_with_results]
                useable_sets.sort()
                for s in useable_sets:
                    self.level_selection.addItem(s)
        elif level == 'Cohort':
            query = "select distinct course_title from courses"
            COURSES = DB.execute(query).fetchall()
            for t in COURSES:
                self.level_selection.addItem(str(t[0]))
        else:
            self.level_selection.addItem('Error!')

        self.update_plot()

    def update_plot(self):
        level = self.levelBox.currentText()
        level_selection = self.level_selection.currentText()
        grouping = self.groupByBox.currentText()
        if grouping == 'Topics':
            group_fields = ['qTopic']
        elif grouping == 'Modules':
            group_fields = ['qModule']
        else:
            group_fields = ['Error!']

        # Filter the data according to the current paramaters
        prepaired_dataframe = self.prepair_data(analysis=level,
                                                tSet=level_selection,
                                                group_fields=group_fields)
        # Repopulate the html view before clearing and reploting the data.
        # The 'barh' plot seems to reverse the order of the data so this
        # re-sorts it into alphabetical order.
        html_dataframe = prepaired_dataframe.sort_index(axis=0, ascending=True)
        html_dataframe = html_dataframe.to_html()
        self.MainArea.htmlArea.setHtml(html_dataframe)

        updated_title_string = 'Viewing data for ' + level_selection
        self.MainArea.plotArea.canvas.axes.cla()
        self.MainArea.plotArea.canvas.plot_data_frame(
                                dataframe=prepaired_dataframe,
                                kind=self.MainArea.plotArea.plot_style,
                                title=updated_title_string)

    def replace_main_widget(self):
        global overviewWidget
        main_window = self.session_details["main_window"]
        overviewWidget = OverviewWidget(self.session_details)
        main_window.setCentralWidget(overviewWidget)


class AnalysisMainArea(QtGui.QWidget):
    def __init__(self, dataframe):
        super(AnalysisMainArea, self).__init__()

        self.prepaired_dataframe = dataframe

        self.stackLayout = QtGui.QStackedLayout()
        self.stack = QtGui.QWidget()
        self.stack.setLayout(self.stackLayout)
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

        # This is the plot view of the data
        self.plotArea = PlotWindow(dataframe=self.prepaired_dataframe,
                                   plot_style=plot_style)
        self.switcher.addTab('Plot View')
        self.stackLayout.addWidget(self.plotArea)

        # This is a scrollabel read only text box giving a summary of
        # the datafram as an html table. It should be possible to add
        # to this with more formatting and data as the analysis
        # functionality of ClMATE develops.
        self.htmlArea = QtGui.QTextEdit()
        self.htmlArea.setReadOnly(True)
        self.switcher.addTab('Data View')
        self.stackLayout.addWidget(self.htmlArea)

        self.mainLayout.addWidget(self.stack)
        self.mainLayout.addWidget(self.switcher)
        self.setLayout(self.mainLayout)
        self.switcher.connect(self.switcher,
                              QtCore.SIGNAL("currentChanged(int)"),
                              self.tabSwitch)

    def tabSwitch(self):
        # This function will take the current tab index and match
        # the central widget index to it in order to swap tabs.
        self.stackLayout.setCurrentIndex(self.switcher.currentIndex())


class PlotWindow(QtGui.QWidget):
    def __init__(self, dataframe, plot_style='barh', parent=None):
        super(PlotWindow, self).__init__()
        self.initUI()

        self.dataframe = dataframe
        self.plot_style = plot_style

        # Set plot details before plotting
        plt.tight_layout()
        plt.close()

    def initUI(self):
        font = {'family' : 'mono',
        'weight' : 'light',
        'size'   : 6}
        matplotlib.rc('font', **font)
        self.canvas = PlotCanvas(self)


class PlotCanvas(FigureCanvas):
    def __init__(self,
                 parent=None,
                 width=DEFAULT_PLOT_WIDTH,
                 height=DEFAULT_PLOT_HEIGHT,
                 dpi=DEFAULT_PLOT_DPI,
                 ylabel='',
                 xlabel='Percentage of marks obtained'):
        pWidth = parent.frameSize().width() / dpi
        pHeight = parent.frameSize().height() / dpi
        self.fig = plt.figure(figsize=(pWidth, pHeight),
                              dpi=dpi,
                              tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        self.xlabel = xlabel
        self.ylabel = ylabel

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_data_frame(self, dataframe, **kwargs):
        output_plot = dataframe.plot(ax=self.axes, **kwargs)
        output_plot.set_xlabel(self.xlabel)
        output_plot.set_ylabel(self.ylabel)
        self.draw()
