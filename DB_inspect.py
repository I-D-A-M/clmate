#! C:\Python34\pythonw
# -*- coding: utf-8 -*-

import os
import sqlite3
# This will need to be a user defined path for when ClMATE gets distributed!
#os.chdir('R:\ClMATE2.0\Code')
DB = sqlite3.connect('ClMATE_DB.db')
# -- Dump the current database to a text file for back up and review
while True:
    decision = input("--> Would you like to dump the current database to a text file? (y/n)")
    if decision == 'y':
        print('Generating a dump file of ALL current data: this will be saved into the ClMATE_output_files directory as ClMATE_data_dump.txt')
        with open('ClMATE_data_dump.txt', 'w') as f:
            f.write('\n\n\nNEW DUMP OUTPUT\n\n')
            for line in DB.iterdump():
                f.write('%s\n' % line)
        break
    elif decision == 'n':
        break
    else:
        print("--> Error:: (y/n) answer is required")
print("Chatting with ClMATE: won't be a tic...")
# -- Set up default queries
staffing = DB.execute('select * from staffing').fetchall()
staff = DB.execute('select * from staff').fetchall()
cohort = DB.execute('select * from cohort').fetchall()
courses = DB.execute('select * from courses').fetchall()
modules = DB.execute('select * from modules').fetchall()
assessments = DB.execute('select * from assessments').fetchall()
assignedTests = DB.execute('select * from assignedTests').fetchall()
assessmentDocs = DB.execute('select * from assessmentDocs').fetchall()
gradeBoundaries = DB.execute('select * from gradeBoundaries').fetchall()
pupilNotes = DB.execute('select * from pupilNotes').fetchall()
# -- Find a way to auto list these incase we want to add more...
print("OK. Now we're ready...")
print("Available queries are: staffing, staff, cohort, courses, modules, assessments, assignedTests, assessmentDocs, gradeBoundaries,pupilNotes")
print("Please call 'f_out(query)' with your chosen query for a formatted output.")

# -- Formatted outputs
def f_out(table_name):
    for query in table_name:
        print(query)
