'''
-- Author:       I.D.A-M
-- Twitter:      @InnesMorrison
-- PyVersion:    Python3.x
-- Dependencies: Pandas, Matplotlib, openpyxl, numpy, pdfkit

This should generate individualised pupil reports with the option to select an agrigation mode.
To be launched from the analysis tab within clmate under 'pupil performance'.

Generation of a PDF for printing is currently being handled by pdfkit [https://pypi.python.org/pypi/pdfkit]
This has been tested on linux (linux mint 17) but not on any other OS.
-- This depends on the wkhtmltopdf library/executable [http://wkhtmltopdf.org/]. This will need to be bundled.

Look at using PyQt4's QWebView class to display arbitrary html content as a way of showing the analysis
output from pandas. [http://www.pythoncentral.io/pyside-pyqt-tutorial-qwebview/]
[http://pyqt.sourceforge.net/Docs/PyQt4/qwebview.html#details]
'''
import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import openpyxl as opx
import matplotlib.pyplot as plt

from .helpers import percentage_marks, pdf_export


def get_master_DataFrame():
    '''
    Read in the pupil data from the database as a Pandas DataFrame in order to allow Pythonic
    data analysis without relying on SQL queries.

    Arguments:
      None
    Returns:
      A Pandas DataFrame.
    '''
    with sqlite3.connect("ClMATE_DB.db") as con:
        results = pd.read_sql("SELECT * from results", con)
        assessments = pd.read_sql("SELECT * from assessments", con)
        merged = pd.merge(results, assessments, how='left', left_on=['aID', 'qNum'], right_on=['aID', 'qNum'])
        merged = merged.drop(['aName_y', 'qTitle', 'aName_x', 'course', 'course_ID', 'module_ID'], axis=1)
        merged['pObt'] = np.vectorize(lambda x, y: (x / y) * 100)(merged['pMark'], merged['qMark'])
        cols = ['UPN', 'aID', 'qNum', 'qModule', 'qTopic', 'pMark', 'qMark', 'pObt', 'teaching_set']
        master_df = merged[cols]
        master_df.rename(columns={'qTopic': 'Topic', 'qModule': 'Module'}, inplace=True)
    return master_df


def generate_results(MASTER_DF=None, tSet=None):
    '''
    Slice the master DataFrame for the required class, and display the results within ClMATE.

    Arguments:
      MASTER_DF -- A Pandas DataFrame containing all of the results data for the cohort.
      tSet      -- The selected teaching set to run analysis on. This is to ensure that
                   teachers can only request data for their own classes.
    Returns:
      None
    '''
    with sqlite3.connect("ClMATE_DB.db") as con:
        class_df = MASTER_DF[MASTER_DF["teaching_set"].isin([tSet])]
        upns = class_df["UPN"].unique()
        query = '"' + tSet + '"'
        names = pd.read_sql('SELECT Name, UPN from cohort WHERE teaching_set = {}'.format(query), con)

        name_df = pd.merge(class_df, names, how='left', left_on=['UPN'], right_on=['UPN'])
    name_list = list(names["Name"])

    writer = pd.ExcelWriter('Output.xlsx')
    for n in name_list:
        pupil_df = name_df[name_df["Name"].isin([n])]
        pupil_grouped = pupil_df.groupby(['Module', 'Topic'])

        # Sum up ALL results for each bin and compute a percentage success rate
        psummary_df = pupil_grouped.sum()
        psummary_df = psummary_df[['pMark', 'qMark']]

        psummary_df['Best Sitting'] = np.vectorize(percentage_marks)(psummary_df['pMark'], psummary_df['qMark'])
        # psummary_df.sort(['sRate'], axis=0, ascending=1, inplace=True)
        psummary_df.rename(columns={'pMark': 'Mark', 'qMark': 'Available'}, inplace=True)

        bplot = psummary_df["Best Sitting"].plot(kind='barh', figsize=(10,8), title="Data for {}".format(n))
        fig = bplot.get_figure()
        figname = "{}.jpg".format(n)
        fig.savefig(figname, transparent=False, bbox_inches='tight')
        bplot.cla()

        psummary_df.to_excel(writer, n)
    writer.save()
    return name_list


def export_to_pdf(file_name, whole_class=True, ):
    '''
    Save the current displayed data as a PDF for printing / emailing.

    Arguments:
      file_name   -- User supplied filename.
      whole_class -- Boolean check on whether the user wants all pupils or
                     just the currently selected one.
    Returns:
      None.
    '''
    html_string = ''
    if whole_class:
        for pupil in tSet:
            # grab HTML representation and append to html_string
            pass
    else:
        # Grab the single representation and append to html_string
        pass
    success, error_reason = pdf_export(html_string, file_name)
    if success:
        if file_name.endswith('.pdf'):
        file_name = file_name[:-4]
        os.startfile('{}.pdf'.format(file_name)
    else:
            QtGui.QMessageBox.question(
            "File creation was unsuccessful",
            error_reason)


def insert_images(tSet, namelist):
    wb = opx.load_workbook('Output.xlsx')

    for num, name in enumerate(name_list):
        ws = wb.worksheets[num]
        img = opx.drawing.Image('{}.jpg'.format(name))
        img.anchor(ws.cell('H5'))
        ws.add_image(img)
        wb.save('{}_summaries.xlsx'.format(tSet))


def clean_up():
    '''
    Remove temp files after compilation into a single .xlsx.
    '''
    for name in name_list:
        os.remove('{}.jpg'.format(name))
    os.remove('Output.xlsx')


if __name__ == '__main__':
    '''
    Execution of this module should be as follows:
    1)  Rip the data from the database into a master DataFrame. This should be limited by the
        users permission level.
    2)  Take a selected teaching-set from the user (via a QT combobox in the final program)
    3)  Filter the DataFrame for only that class and display a list of pupils to the user in the
        sidebar.
    4)  For the current combobox, display an HTML view of the pupil data and output graph.
    5)  For this data, allow filtering of individual assessments, best/mean/worst sitting etc.
        NOTE -- This functionality needs to be consistent accross both this screen and the overall
                class view.
    6)  Also need to support exporting to PDF via pdfkit. This is handled by helpers.py.
    '''
    tSet = '10-IM 14/15'
    master = get_master_DataFrame()
    generate_results(master, tSet)
