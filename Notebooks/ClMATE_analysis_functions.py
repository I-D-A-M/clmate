from collections import namedtuple
import pandas as pd
import numpy as np
import sqlite3


def get_results(teaching_set=None, DBname="ClMATE_DB.db"):
    '''
    Pull results from the ClMATE database for the specified teaching set.
    This is then used to create a master dataframe for use within the Notebook.

    NOTE: it is also possible to store read in an example CSV file to try everything out.
    '''
    if not teaching_set:
        print("WARNING: Teaching set was not suppplied.")
        return "Things went wrong...."
    with sqlite3.connect(DBname) as DB:
        query = "SELECT * FROM results WHERE teaching_set = ?"
        # -- Format is: aID; UPN; teaching_set; aName; qNum; pMark
        res = DB.execute(query, (teaching_set,)).fetchall()
        # -- prep question mark data for combining into the result tuples
        assessmentMarks = dict()
        assessmentIDs = set([r[0] for r in res])
        for a in assessmentIDs:
            query = "SELECT qNum, qMark from assessments where aID = ?"
            qScores = DB.execute(query, (a,)).fetchall()
            for q in qScores:
                key = str(a) + '/' + str(q[0])
                assessmentMarks[key] = q[1]
    # -- Improve readability for main dataset: class_results should NOT be mutated
    result = namedtuple('Result', ['UPN', 'tSet', 'aID', 'qNum', 'mark', 'total'])
    class_results = [result(r[1], r[2], r[0], r[4], r[5], assessmentMarks[str(r[0]) + '/' + str(r[4])]) for r in res]
    return class_results


def get_name(UPN):
    ''' Given a valid UPN, return the student's name in the database. '''
    with sqlite3.connect("ClMATE_DB.db") as DB:
        q = "SELECT name FROM cohort where UPN = ?"
        name = DB.execute(q, (UPN,)).fetchone()
    return name[0]


def get_question_names(aIDs=list()):
    ''' Return the question titles for a given list of assessment IDs as a dict.'''
    titleDict = dict()
    for aID in aIDs:
        aID = int(aID)
        titleDict[aID] = dict()
        with sqlite3.connect("ClMATE_DB.db") as DB:
            query = "SELECT qNum, qTitle FROM assessments where aID = ?"
            qTitles = DB.execute(query, (aID,)).fetchall()
            for q in qTitles:
                titleDict[aID][q[0]] = q[1].strip()
    return titleDict


def get_qName(aID, qNum, title_dictionary):
    '''Dict lookup helper for vectorising accross a dataframe'''
    return title_dictionary[aID][qNum]


def get_aNames(aIDs):
    '''Use aID to pull out assessment names from the database.'''
    aNames = list()
    for aID in aIDs:
        aID = int(aID)
        with sqlite3.connect("ClMATE_DB.db") as DB:
            query = "SELECT aName FROM assessments where aID = ?"
            name = DB.execute(query, (aID,)).fetchone()
            aNames.append('{}: {}'.format(aID, name[0]))
    return aNames


def get_module(aID, qNum):
    '''Pull question module allocations given assessment ID and question number.'''
    with sqlite3.connect("ClMATE_DB.db") as DB:
        q = "select qModule from assessments where aID = ? and qNum = ?"
        topic = DB.execute(q, (int(aID), int(qNum))).fetchone()
    return topic[0]


def get_FFT(name):
    '''Find a pupil's FFT given their name in the database.'''
    with sqlite3.connect("ClMATE_DB.db") as DB:
        q = "select FFT from cohort where Name = ?"
        FFT = str(DB.execute(q, (name,)).fetchone()[0])
    return FFT


def get_tier(tSet):
    '''Find the course that the class is on.'''
    with sqlite3.connect("ClMATE_DB.db") as DB:
        q = "select course from staffing where teaching_set = ?"
        tier = str(DB.execute(q, (tSet,)).fetchone()[0])
    return tier


def get_master_dataframe(selected_classes=list(), demo=False):
    ''' Pull in data from the ClMATE database and set up a master dataframe.
        By default, this has the following layout:
        Name	tSet	aID	tier	FFT	qNum	module	topic	mark	total	Qperformance%
    '''
    if not demo:
        ''' Retrieve all results for the selected classes and format as a Pandas Dataframe. '''
        all_results = list()
        for tSet in selected_classes:
                r = get_results(teaching_set=tSet, DBname="ClMATE_DB.db")
                if len(r) != 0:
                    all_results += r
                else:
                    print("WARNING - Could not load data for the following class:\n\t{}".format(tSet))

        resultsDF = pd.DataFrame(all_results, columns=all_results[0]._fields)
        resultsDF['Name'] = resultsDF['UPN'].apply(get_name)
        resultsDF['Qperformance%'] = np.round(resultsDF['mark'] / resultsDF['total'], 2) * 100
        titleDict = get_question_names(list(resultsDF.aID.unique()))
        resultsDF['topic'] = np.vectorize(get_qName)(resultsDF['aID'], resultsDF['qNum'], titleDict)
        resultsDF['module'] = np.vectorize(get_module)(resultsDF['aID'], resultsDF['qNum'])
        resultsDF['FFT'] = np.vectorize(get_FFT)(resultsDF['Name'])
        resultsDF['tier'] = np.vectorize(get_tier)(resultsDF['tSet'])

        resultsDF = resultsDF[['Name', 'tSet', 'aID', 'tier', 'FFT', 'qNum', 'module', 'topic', 'mark', 'total', 'Qperformance%']]
        resultsDF.replace(to_replace='Ratio, Proportion & Rates of Change', value='RPR', inplace=True)
        # Print summary of the retrieved data for the user
        aNames = get_aNames(list(resultsDF.aID.unique()))
        print('\nData fetched for the following assessments\n\t{}'.format('\n\t'.join(aNames)))
    else:
        resultsDF = pd.DataFrame.from_csv("demo.csv")
    return resultsDF


def savePlot(DF=None, test=False, selectedClass=None, aID=None):
    '''Save a pupil bar chart to disk.'''
    if (selectedClass is None) or (aID is None) or (len(DF) == 0):
        print('ERROR: you must provide a class and assessment ID to generate Histograms')
        return

    frame = DF[DF.tSet == selectedClass]
    frame.Name.reset_index(drop=True, inplace=True)    # Needed as the original index from the dataframe is kept!
    frame['perc'] = frame['mark'] / frame['total'] * 100
    pupilDF = frame[['Name', 'aID', 'qNum', 'perc']]
    for name in pupilDF.Name.unique():
        toPlot = pupilDF[(pupilDF['Name'] == name) & (pupilDF['aID'] == aID)]
        toPlot.columns = ['Name', 'aID', 'Question', '% Marks Obtained']
        diag = toPlot.plot(x='Question', y='% Marks Obtained', kind='bar', title='% performance by question', legend=False, figsize=(8, 5))
        fig = diag.get_figure()
        figname = "{}_{}.png".format(name.replace(" ", "_"), aID)
        fig.savefig(figname, transparent=False, bbox_inches='tight')
        diag.cla()
        if test:
            break    # Break after the first pupil so we can check output quickly
