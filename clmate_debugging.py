#! C:\Python34\pythonw
# -*- coding: utf-8 -*-

import warnings
from PyQt4 import QtGui, QtCore
import sqlite3
import time
import sys
import os

import ClMATE

#######################################################
# THIS MAY SKREW THINGS UP! IF THINGS ARE GOING WRONG #
# DISABLE THIS FIRST AND CHECK THE CONSOLE OUTPUT     #
#######################################################
''' This line - as you might expect - disables all console
based warnings that are thrown using the warnings module.
These can cause problems when running ClMATE as a .pyw file.'''
warnings.filterwarnings("ignore")


################################################################################
# This is the main function body for ClMATE #
#############################################

def main():
    '''
    ClMATE is a pupil data management system with the ability to pull data from
    SIMS.net to speed up initial setup. Admin accounts are able to set test
    assigned to individual classes or to a full cohort in addition to running
    both broad and fine detail reports on test data. Class teacher accounts can
    view and enter test results on assigned classes and can also run simple
    reports on their classes/pupils.
    '''
    global main_window
    # -- Required in order for Windows to accept an app icon other than Python's
    if sys.platform == 'win32':
        import ctypes
        appid = 'ClMATE.version.2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QtGui.QApplication(sys.argv)
    icon = QtGui.QIcon('ClMATE/resources/logo.png')
    app.setWindowIcon(icon)
    splash_pic = QtGui.QPixmap()
    splash_pic.load('ClMATE/resources/splash.png')
    splash = QtGui.QSplashScreen(splash_pic, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pic.mask())
    splash.show()
    app.processEvents()
    splash.showMessage( "Now loading ClMATE: Close Monitoring and Analysis "
                        "Tool for Educators.\nVersion:: "
                        + ClMATE.program_version + "   " + chr(0xa9)
                        + " I.Morrison 2014/15.\n"
                        + ClMATE.py_v_message,
                        alignment=0x0044,
                        color=ClMATE.white)
    app.processEvents()

    # -- Set up custom fonts
    app.fontDB = QtGui.QFontDatabase()
    app.fontDB.addApplicationFont('ClMATE/resources/fonts/Sertig.otf')
    app.fontDB.addApplicationFont('ClMATE/resources/fonts/AmaticSC-Regular.ttf')
    app.fontDB.addApplicationFont('ClMATE/resources/fonts/JosefinSans-Regular.ttf')
    # Source Sans Pro / AR BONNIE
    appFont = QtGui.QFont('Source Sans Pro', 10, weight=20)
    appFont.setStyleStrategy(QtGui.QFont.PreferAntialias)
    app.setFont(appFont)
    # -- uncomment to view the call name for each font that has been added
    #print(app.fontDB.families())

    main_window = ClMATE.MainWindow()
    time.sleep(1)
    login_box = ClMATE.LoginBox(DBname, main_window)
    splash.finish(main_window)
    sys.exit(app.exec_())


if __name__ == "__main__":
    DBname = ClMATE.DBname
    if not os.path.exists(DBname):
        from ClMATE.helpers import createDB
        createDB()
        #ftw = firstTimeWizard()
    main()
