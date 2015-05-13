from .bases import StdWindow
from PyQt4 import QtGui
import sqlite3
import time


class LoginBox(StdWindow):
    '''
    At present there is no crypto employed to secure acccess to the database and all user
    login details are stored within the same database as pupil and course data.
    '''
    def __init__(self, database_file_location, target_main_window):
        super(LoginBox, self).__init__()
        self.DBname = database_file_location
        self.main_window = target_main_window
        self.initUI()

    def initUI(self):
        self.resize(300, 120)
        global userbox, passbox
        user = QtGui.QLabel('Username')
        passw = QtGui.QLabel('Password')
        self.userbox = QtGui.QLineEdit()
        self.userbox.setPlaceholderText("Username")
        self.passbox = QtGui.QLineEdit()
        # -- Hide user input in the password field
        self.passbox.setEchoMode(QtGui.QLineEdit.Password)
        self.passbox.setPlaceholderText("Password")
        loginbtn = QtGui.QPushButton('Login', self)
        # -- Attempt login on Return or on user click of the login button
        loginbtn.clicked.connect(self.logincheck)
        self.userbox.returnPressed.connect(self.logincheck)
        self.passbox.returnPressed.connect(self.logincheck)
        loginbtn.setToolTip(
                "Contact your head of department if "
                "you can not remember your password.")
        loginbtn.resize(loginbtn.sizeHint())
        # -- Selection box to allow password change
        self.change_pass = QtGui.QCheckBox('Change password')
        self.change_pass.stateChanged.connect(self.add_pass_change)
        # -- Set up a grid to position UI elements
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(1)
        self.grid.addWidget(user, 1, 0)
        self.grid.addWidget(self.userbox, 1, 1, 1, 2)
        self.grid.addWidget(passw, 2, 0)
        self.grid.addWidget(self.passbox, 2, 1, 1, 2)
        self.grid.addWidget(loginbtn, 3, 2)
        self.grid.addWidget(self.change_pass, 3, 0)
        self.setLayout(self.grid)
        super(LoginBox, self).initUI()

    def add_pass_change(self):
        '''
        If the user want's to change their password this function
        provides two text boxes to confirm the new password with.
        '''
        # -- User is changing their password
        if self.change_pass.checkState():
            self.passbox.setPlaceholderText("Old Password")
            self.pass_changer = QtGui.QLineEdit()
            # -- Hide user input
            self.pass_changer.setEchoMode(QtGui.QLineEdit.Password)
            self.pass_changer.setPlaceholderText('New Password')
            self.pass_confirmer = QtGui.QLineEdit()
            # -- Hide user input
            self.pass_confirmer.setEchoMode(QtGui.QLineEdit.Password)
            self.pass_confirmer.setPlaceholderText('Confirm New Password')
            self.grid.addWidget(self.pass_changer, 4, 0, 1, 2)
            self.grid.addWidget(self.pass_confirmer, 5, 0, 1, 2)
        # -- Replace original layout and placeholder text
        else:
            self.passbox.setPlaceholderText("Password")
            self.grid.removeWidget(self.pass_changer)
            self.pass_changer.deleteLater()
            self.grid.removeWidget(self.pass_confirmer)
            self.pass_confirmer.deleteLater()

    def logincheck(self):
        '''
        User entered details are compared against database records: if login is
        successful then the session username and permission levels are set.
        '''
        global username, password, permissionLevel
        username = str(self.userbox.text()).lower()
        password = str(self.passbox.text())

        DB = sqlite3.connect(self.DBname)
        with DB:
            user_query = "select username from staff where username = ?"
            validuser = DB.execute(user_query, (username,))
            pass_query = "select password from staff where username = ?"
            validpass = DB.execute(pass_query, (username,))
            if validuser.fetchone():
                validpass = validpass.fetchone()[0]
                if validpass == password:
                    if self.change_pass.checkState():
                        new_pass = str(self.pass_changer.text())
                        pass_conf = str(self.pass_confirmer.text())
                        if new_pass == pass_conf:
                            query = ("update staff set password = ? "
                                     "where username = ?")
                            DB.execute(query, (new_pass, username))
                            DB.commit()
                            success = QtGui.QMessageBox.question(
                                            self,
                                            "Success",
                                            "Password Updated")
                        else:
                            failure = QtGui.QMessageBox.question(
                                            self,
                                            "Password Change Unsuccessful",
                                            "New password entry did not match")
                    # -- Set permission level and launch the main window
                    query = "select account_type from staff where username = ?"
                    permissionLevel = DB.execute(query,
                                                 (username,)).fetchall()[0][0]

                    # -- This is a dictionary that will be passed to the main window
                    #    in order to inject session details for use within other
                    #    parts of the program.
                    session_details = {"username": username,
                                       "permissionLevel": permissionLevel,
                                       "DBname": self.DBname,
                                       "main_window": self.main_window}
                    self.close()
                    with open('clmate_log.txt', 'a') as log:
                        print("{} logged in on {}".format(username, time.ctime()), file=log)
                    self.main_window.initUI(session_details)
                # -- Password error
                else:
                    failure = QtGui.QMessageBox.question(
                                        self,
                                        "Login Unsuccessful",
                                        ("The password you entered was not valid."
                                         "\n(Please try again or contact your "
                                         "head of department.)"))
            # -- Username error
            else:
                failure = QtGui.QMessageBox.question(
                                        self,
                                        "Login Unsuccessful",
                                        ("The password you entered was not valid."
                                         "\n(Please try again or contact your "
                                         "head of department.)"))
        DB.close()
