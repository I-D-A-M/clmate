This version of ClMATE should work in exactly the same way as the original
but ideally be more maintainable. In addition to purging all global variables
the existing program will be broken up into the following modules:

    readme.md
    clmate.pyw
    __init__.py
    bases.py
    helpers.py
    login.py
    main_w.py
    main_interface.py
    data_entry.py
    analysis.py
    admin_panel.py
    [first_time_wizard.py]
    creators.py
    [db_manager.py]
    [plugin_manager.py]
    [user_preference.py]

The aim of this is to increase code readability and modularity; reduce
redundancy in the codebase and prepare for integrated testing.


--------------------------------------------------------------------------------
-- Building ClMATE with Py2exe --
---------------------------------

In order to have ClMATE function correctly when using Py2exe to build a single
.exe a little juggling is required:

Py2exe should be run from the local directory with the following flags,

    py -3.4 -m py2exe.build_exe clmate.pyw -c --bundle-files 3

At present, the createDB function is hard coded to use specified .xlsx files and
will crash if they are not found within the same directory as clmate.exe. If a
pre-existing database is copied into the directory then this can be used as
normal.
In order to get the resources to load correctly you will also need to create a
folder named "ClMATE" in the newly created dist directory and copy in the
resources folder from the source tree. After this, ClMATE should run identically
to when it is run a script through the Python interpreter.
--------------------------------------------------------------------------------

ClMATE - Close Monitoring and Analysis Tools for Educators

The following code has been written to adapt and extend the work done
by C.Stephenson with the ClMATE spreadsheet to provide teachers with
a lightweight, easy to use interface for recording and analysing pupil
attainment data. Multiple access levels are possible through admin
accounts allowing heads of departments to set and manage courses for
their staff. Initial set up can take a .xlsx output from SIMS.net in
order to automate the import of pupil details. If desired, ClMATE is
capable of exporting results data and analysis in a formatted .xlsx
file for printing and further analysis.

All data created with ClMATE is kept within a local directory SQLite3
database. Please note that ClMATE can be run on either Python2.X or
Python3.X provided that all external libraries are present and currently
located in the working directory: no additional installation is required.

All work is copyright I.Morrison 2014/15.
contact: @MrMorrisonMaths [Twitter]

================================================================================
External Libraries

PyQt4:: http://www.riverbankcomputing.co.uk/software/pyqt/download
> QtCore and QtGui modules are required to create the GUI interface of ClMATE.

Numpy:: http://www.numpy.org/
> High speed numerical computation.

Pandas:: http://pandas.pydata.org/
> Efficient data analysis and manipulation.

MatplotLib:: http://matplotlib.org/
> Plotting and graphical representation of data.

Openpyxl:: http://openpyxl.readthedocs.org/en/latest/
> Read and write capability for .xls / .xlsx including rich formatting
  of the generated spreadsheet. NOTE: openpyxl requires jdcal in order to run.

pydoc -w::
    Used to generate HTML documentation for ClMATE

py2exe:: http://www.py2exe.org/
> See https://pypi.python.org/pypi/py2exe/0.9.2.0 for details of use with
  Python3.
  NOTE:: GUI based programs can only be built with either bundle=3 or 2

  py -3.4 -m py2exe.build_exe clmate.pyw -c --bundle-files 3


================================================================================
PROJECT PROGRESS [Project began 29/9/2014]

-- NOTE on version numbers::
[Release version].[major update / break compatibility].[minor update / bugfix]

[0.0.1] Main window UI and login box working [5/10/14]

[0.0.2] Database UI test successful {dbtest.py} and integration into main
        program now beginning [14/10/14]

[0.0.3] Login check now refers to a database table of login details and
        has a warning popup if the login is unsuccessful [15/10/14]
[0.0.4] Class tabs are now populated based on available data including
        generation of class names and filtering out duplicate class tabs
[0.0.5] Added support for admin/user profiles and removal of admin options
        from standard user interface
[0.0.6] Started looking at assigning staff to sets via the staffing table
        -> only taught sets now show on login
[0.0.7] Can now correctly read in pupil data from .xls [20/10/14]
[0.1.0] Assessment creator now with basic functionality [1/11/14]
[0.1.2] Viewing of stored assessments added [2/11/14]
[0.1.3] Result entry screen coded and now working on saving to DB [18/11/14]
[0.1.4] BUGFIX: Assigning several assessments results in only the last
        assessment updating via update_summaries()
        -> problem was with referencing elements of the stackLayout
[0.1.5] Results are colour coded, course and assessment creation wizards
        are complete [25/11/14]
[0.1.6] BUGFIX: Pupils with no target crashed the InputWindow [27/11/14]
        -> now default to N/A if no target is found
[0.2.0] Removed dependency on QtSql module as this seemed to be the one
        that requires extra dlls [28/11/14]
        New database feature:: ID fields to prevent name clashes
[0.2.1] BUGFIX: Incorrect grade boundaries being used with
        update_summaries() [29/11/14]
        -> Implemented grade_dict_list and boundary_list to keep track of
           the multiple boundaries being created.
[0.2.2] BUGFIX: Mismatch between class targets and assessment boundaries
                caused the InputWindow to crash [30/11/14]
        -> Default to targets being lowest grade if this is the cases
[0.2.3] BUGFIX: Implemented a warning and disabled grade fields when
                there was a key error via self.GRADE_COMP_ENABLED [30/11/14]
        -> This happens when InputWindow  is created and update_summaries()
           then ignores relative grade details.
[0.2.4] Added access to the system clipboard when entering marks through
        the InputWindow widget [1/12/14]
[0.2.5] BUGFIX: When copying from a spreadsheet a null-string is appended
        to the end of the selection
        -> Skip pasting of last row if it is null [allows copy/paste within
           ClMATE as well] [2/12/14]
[0.3.0] Refactored the update_summaries() function in order to improve
        performance: now runs ONLY for edited cells and their related
        summaries.
        Improvement: For a class of 27 pupils on a 10 question assessment
                     pasting in a new mark for every cell:
                     [0.6.5] - 93.81199717521667 seconds
                     [0.6.6] - 1.0459988117218018 seconds
                     -->  89.7 times faster!
[0.3.1] Implemented an admin level override mode to allow data entry
        for any class [3/12/14]
[0.3.2] Added top/bottom three questions by % to the quick overview [7/12/14]
[0.3.3] Reworked the UI and added an 'About ClMATE' pop-up. [29/12/14]
[0.4.0] Added first pass at the analysis section providing full cohort
        overview for an assessment. [7/1/15] [NOW REMOVED]
[0.4.1] Analysis section completely re-written using numpy and pandas. At
        present we can now view a summary - by class - of modules and topics
        by either mean average or best sitting. Currently working on
        implementing this for individual pupils including a search feature
        via fuzzy matching [20/2/15]
[0.4.2] Changed file extension to .pyw in order to run without an additional
        console window being opened by the system. [24/2/15]
        --> At the moment, warnings are being ignored in order to allow this
            to function correctly. It will probably be a good idea to catch
            and store these in a log at some point.
[0.4.3] Brought codebase into compliance with Pep8 [25/2/15]
[0.5.0] Code base has now been split into use specific files as outlined
        at the head of this readme file. Initial changes are as follows:
        -> There is now a "session_details" dictionary that is passed
           between instances in order to maintain and manage global details.
           -> This is explicitly passed as a parameter to the __init__
              method of each class that requires access to the data.
        -> Most of the pre-existing global variables have been removed in
           favor of the session_details method outlined above.
        -> There is a module level definitions file that will eventually
           allow for user settings and easy alteration of program
           parameters. [12/3/15]
[0.5.1] Modified data_entry.py commit_to_DB() to improve efficiency. (SQLite
        based improvements.) and added simple logging of user activity. [3/5/15]
[0.5.2] Modified database accesses to use context managers and close all
        connections immediately on completion of read/write. [7/3/15]
=================================================================================
TODO

RE-FACTORING::

When loading the assessments they should be created on the fly NOT
stored in memory as this will create a MASSIVE amount of objects!
Default boundaries set at course creation
  Also allow assessment templates of: pass/fail (set pass mark)
                                      admin (complete/pending)
                                      [eventually have premade templates]
In addition to the 'Overview' dump it should be possible to generate a
pupil analysis sheet. [record marks, topic scores, set targets etc]
Viewing test question breakdowns::
  Look at data analysis and display modules {numpy, panda, matplotlib}
  A*-A, A*-B...A*-pass etc
  Above/below APLs (compile list of students and sets)
  SEN and PP vs cohort
Error catching {use TRY, EXCEPT to launch an error window if needed}
  https://docs.python.org/2/tutorial/errors.html for module wide exceptions
'Niceify' the UI::
  settings panel
  colour schemes [http://www.colorschemer.com/online.html]
  font/display sizes
Help documentation
First time setup wizard

================================================================================
STYLE GUIDE

Line length for ClMATE code is 90(ish) characters. A few characters over is fine
but line lengths significantly over 90 should be split.
--> The preferred method of splitting Sqlite3 queries is to define the query string
    on the preceding line as "query"; using implicit line joining via parens if
    required.

Indents are 4 spaces.

Classes are named using CamelCase.
Functions are named using mixedCase.
Variables are named using under_scores.

ALL connections to the database are to be carried out via context managers and explicit
closing of the connection after each transaction.

Where possible use "DB.row_factory = sqlite3.Row" to allow for a dictionary like
interface with queries in order to improve readability.

=================================================================================
LOGGING

User access to the database is logged using the following code:

with open('clmate_log.txt', 'a') as log:
    print("{} logged in on {}".format(username, time.ctime()), file=log)

This should also be used to record any changes to the database including recording
results, creating assessments/courses, setting assessments etc.