# -*- coding: utf-8 -*-
import sys
import pytest
from mock import Mock
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from PyQt4.QtGui import QApplication

from ..login import LoginBox


class Test_login_box():
    app = QApplication(sys.argv)

    mock_main = Mock({"initUI": "Main window UI initialised"})
    login_box = LoginBox("testDB.db", mock_main)

    def set_input_to_default(self):
        self.login_box.userbox.setText("")
        self.login_box.passbox.setText("")

    def test_login_success(self):
        '''
        This should test to see what the response of the login dialogue is. At the moment
        all it does is open the UI and then close it.

        NEED TO ASSERT SOMETHING!
        '''
        self.login_box
        self.login_box.userbox.setText("morrisoni")
        self.login_box.passbox.setText("fail")
        loginbtn = self.login_box.layout().itemAtPosition(3, 2).widget()
        QTest.mouseClick(loginbtn, Qt.LeftButton)
