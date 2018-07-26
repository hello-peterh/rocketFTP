#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 14:42:24 2018

@author: peterhung
"""
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from autoFTP_small import Ui_MainWindow
import os
import os.path
from shutil import copy2
import random
import datetime
import errno
import subprocess
import imaplib
from fetch_emails import FetchEmail
import time
import email

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        print('Initiated rocketFTP')

        #Using UI from Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Open file
        self.ui.actionOpen.triggered.connect(self.open_file)

        #Open file via shortcut
        openFile = QtWidgets.QAction('&Open File', self)
        openFile.setShortcut('cmd+O')
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.open_file)

        #UI DESIGN INIT
        self.ui.btn_connect.clicked.connect(self.connect)
        self.ui.btn_start.clicked.connect(self.promote)
        self.ui.btn_pause.clicked.connect(self.reset)
        self.ui.btn_add.clicked.connect(self.open_file)
        self.ui.btn_autoFetchEmails.clicked.connect(self.fetch_attachments)

        self.ui.lbl_ohost_status.setText('NOT CONNECTED')
        self.ui.lbl_thost_status.setText('NOT CONNECTED')

        self.ui.line_currentfile.setEnabled(False)
        self.ui.btn_pause.setEnabled(False)
        self.ui.btn_start.setEnabled(False)

        self.ui.pushButton_3.clicked.connect(self.open_log)

        iconDir = os.path.dirname(os.path.realpath(__file__))
        #self.setWindowIcon(QtGui.QIcon(iconDir + os.path.sep + 'rocketFTP_logo.png'))
        #print('OVER HERE' + iconDir + os.path.sep + 'rocketFTP_logo.png')
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(iconDir + 'rocketFTP_icon.png')))

        #Open editor
        openEditor = QtWidgets.QAction('&Editor', self)
        openEditor.setShortcut('cmd+E')
        openEditor.setStatusTip('Open Editor')
        openEditor.triggered.connect(self.editor)

        openTester = QtWidgets.QAction('&Generate Random Files', self)
        openTester.setShortcut('cmd+T')
        openTester.setStatusTip('Open Tester')
        openTester.triggered.connect(self.tester)
        
        #MENU
        mainMenu = self.menuBar()

        editorMenu = mainMenu.addMenu('&Editor')
        editorMenu.addAction(openEditor)

        testerMenu = mainMenu.addMenu('&Tester')
        testerMenu.addAction(openTester)

        self.ui.rad_auto.setChecked(True)

        #COMBO BOX ENVIRONMENTS
        #self.ui.combo_ohost.currentIndexChanged(

        #GLOBAL VARIABLES
        global request_lst
        request_lst = []
        
        global masterfile_lst
        masterfile_lst = []

        global host_dict
        host_dict = {'Bronze': '/stecontent',
                        'Silver': '/stagingcontent',
                        'Production' : '/livecontent',
                        'Local': '/local'}

        global ready
        ready = 0

        global rootdir
        rootdir = '/Users/peterhung/Personal Projects/autoFTP/promotions-test/stecontent'
        global rootdir2
        rootdir2 = '/Users/peterhung/Personal Projects/autoFTP/promotions-test/logs/'

        global requestor
        requestor = ''

        global request_model
        request_model = QtGui.QStandardItemModel(self.ui.list_input)

    def tester(self):

        n = 5
        
        for i in range(n): 
            test_file = 'webpage'
            for j in range(5):
                rand_num = random.randint(0,9)
                test_file += str(rand_num)
            
            completeFile = os.path.join(rootdir, test_file+'.txt')
            outfile = open(completeFile, 'w')
            outfile.write('This is a test for file: ' + test_file)

    def editor(self):
        self.textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(self.textEdit)

        self.setGeometry(50, 50, 300, 600)

    def connect(self):

        try:
            if masterfile_lst == []:
                self.ui.btn_start.setEnabled(False)
            else:
                self.ui.btn_start.setEnabled(True)

            self.ui.combo_ohost.setEnabled(False)
            self.ui.combo_thost.setEnabled(False)
            self.ui.rad_auto.setEnabled(False)
            self.ui.rad_binary.setEnabled(False)
            self.ui.rad_other.setEnabled(False)
            self.ui.list_input.setEnabled(False)
            self.ui.btn_connect.setText('Connected')
            self.ui.btn_connect.setEnabled(False)

            self.ui.lbl_ohost_current.setText(self.ui.combo_ohost.currentText())
            self.ui.lbl_thost_current.setText(self.ui.combo_thost.currentText())
            self.ui.lbl_ohost_status.setText('OK')
            self.ui.lbl_thost_status.setText('OK')
            self.ui.lbl_ohost_status.setStyleSheet('color: green')
            self.ui.lbl_thost_status.setStyleSheet('color: green')

            self.ui.btn_pause.setEnabled(True)

            if self.ui.combo_ohost.currentText() == 'Automatic':
                self.ui.combo_thost.setCurrentText('Automatic')

                for line in text:
                    if "FROM:" in line:
                        oHost = line[line.rfind(':')+1:]
                        self.ui.lbl_ohost_current.setText(oHost)

                    if "TO:" in line:
                        tHost = line[line.rfind(':')+1:]
                        self.ui.lbl_thost_current.setText(tHost)
        except:
            print('Requires a file')


    def reset(self):
        self.ui.combo_ohost.setEnabled(True)
        self.ui.combo_thost.setEnabled(True)
        self.ui.rad_auto.setEnabled(True)
        self.ui.rad_binary.setEnabled(True)
        self.ui.rad_other.setEnabled(True)
        self.ui.list_input.setEnabled(True)
        self.ui.btn_connect.setText('Connect')
        self.ui.btn_connect.setEnabled(True)

        self.ui.lbl_ohost_current.setText(self.ui.combo_ohost.currentText())
        self.ui.lbl_thost_current.setText(self.ui.combo_thost.currentText())
        self.ui.lbl_ohost_status.setText('NOT CONNECTED')
        self.ui.lbl_thost_status.setText('NOT CONNECTED')
        self.ui.lbl_ohost_status.setStyleSheet('color: black')
        self.ui.lbl_thost_status.setStyleSheet('color: black')

        self.ui.progressBar.setValue(0)

        self.ui.btn_pause.setEnabled(False)
        self.ui.btn_start.setEnabled(False)

        try:
            del request_lst[:]
            request_model.clear()
            del masterfile_lst[:]
            print(len(masterfile_lst))
        except:
            print('Clearing an empty list')

        self.ui.line_currentfile.setText('')

    def open_file(self):

        try:
            #STEP 1: Set requests to promote
            name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
            file = open(name[0], 'r')

            #name[0] = /Users/peterhung/Personal Projects/autoFTP/file_promotion_request.txt
            #name[0]name[0][name[0].rfind('/')+1:] = file_promotion_request.txt

            if name[0][name[0].rfind('/')+1:] not in request_lst:
                request_lst.append(name[0][name[0].rfind('/')+1:])

                for item in request_lst:
                    print(item)
                    item_m = QtGui.QStandardItem(item)
                    item_m.isCheckable()
                    item_m.setCheckState(True)
                    request_model.appendRow(item_m)

                self.ui.list_input.setModel(request_model)
            else:
                print('ALREADY IN LIST')

            #STEP 2: Build into a master list of items to promote (NOT THE ACTUAL REQUEST FILE ITSELF)

            file_lst = []        
            with file:
                global text
                text = file.read().split('\n')

            if self.ui.combo_ohost.currentText() == 'Automatic':
                self.ui.combo_thost.setCurrentText('Automatic')

                for line in text:
                    if "/" in line:
                        file_lst.append(line)
                    
                    if "FROM:" in line:
                        oHost = line[line.rfind(':')+1:]
                        self.ui.lbl_ohost_current.setText(oHost)

                    if "TO:" in line:
                        tHost = line[line.rfind(':')+1:]
                        self.ui.lbl_thost_current.setText(tHost)
            
            masterfile_lst.append(file_lst)
            print('file list ' + str(len(file_lst)))
            print('master list ' + str(len(masterfile_lst)))
        
        except:
            print('closed window')

    def fetch_attachments(self):

        f = FetchEmail()
        msgs = f.fetch_unread_messages()
            
        for m in msgs:
            file_location = f.save_attachment(
                msg=m,
                download_folder='/Users/peterhung/Personal Projects/autoFTP/tmp'
                )

        f.close_connection()
        self.auto_insert_file()
    
    def auto_insert_file(self):
    
        for f in os.walk('/Users/peterhung/Personal Projects/autoFTP/tmp'):
            for item in f[2]:
                if item == '.DS_Store':
                    pass
                else:
                    print('Downloaded ' + item)

                    file = open('/Users/peterhung/Personal Projects/autoFTP/tmp/'+ item, 'r')
                    
                    if item not in request_lst:
                        request_lst.append(item)
                    else:
                        print(item + ' is already in the list.')

                    file_lst = []        
                    with file:
                        global text
                        text = file.read().split('\n')

                        if self.ui.combo_ohost.currentText() == 'Automatic':
                            self.ui.combo_thost.setCurrentText('Automatic')

                            for line in text:
                                if "/" in line:
                                    file_lst.append(line)

                                if "FROM:" in line:
                                    oHost = line[line.rfind(':')+1:]
                                    self.ui.lbl_ohost_current.setText(oHost)

                                if "TO:" in line:
                                    tHost = line[line.rfind(':')+1:]
                                    self.ui.lbl_thost_current.setText(tHost)
                            
                        masterfile_lst.append(file_lst)

        for i in request_lst:
            item_m = QtGui.QStandardItem(i)
            item_m.isCheckable()
            item_m.setCheckState(True)
            request_model.appendRow(item_m)

        self.ui.list_input.setModel(request_model)

    def promote(self):
        
        rootdir = '/Users/peterhung/Personal Projects/autoFTP/promotions-test/'
        cur_env = self.ui.lbl_ohost_current.text() #host_dict.get(self.ui.lbl_ohost_current.text())
        new_env = self.ui.lbl_thost_current.text() #host_dict.get(self.ui.lbl_thost_current.text())

        success_model = QtGui.QStandardItemModel(self.ui.listView_2)
        fail_model = QtGui.QStandardItemModel(self.ui.listView_3)
        fail_lst = []

        result = []

        for req in masterfile_lst:
            #print(req)

            accum = 0
            item_count = len(req)
            #print('first try:'+ str(item_count))
            try:
                counter = 1/item_count*100
                #print(counter)
            except:
                print('The number of total items = ' + str(item_count))
            
            for line in req:

                for f in os.walk(rootdir + cur_env + line[:line.rfind('/')]):

                    for i in f[2]:
                        if i == line[line.rfind('/')+1:]:
                            try:
                                self.duplicate_file(rootdir + cur_env + line, rootdir + new_env + line)
                                print('Successfully promoted: ' + i)
                                self.ui.line_currentfile.setText(i)

                                accum += counter
                                self.ui.progressBar.setValue(accum)
                                QtWidgets.QApplication.processEvents()

                                #LOG STUFF
                                item_m = QtGui.QStandardItem(new_env + line)
                                success_model.appendRow(item_m)
                                
                                result.append(str(datetime.datetime.now())+ '\t| SUCCESS' + ' | ' + cur_env + '>' + new_env + ' | PATH: ' + line + '\n')
                            except:
                                print('Path in desintation location does not exist.')
                        elif line[line.rfind('/')+1:] not in f[2] and line not in fail_lst:
                            fail_lst.append(line)
                            result.append(str(datetime.datetime.now())+ '\t| FAILED' + '  | ' + cur_env + '>' + new_env + ' | PATH: ' + line + '\n')

            for failed in fail_lst:
                item_f = QtGui.QStandardItem(failed)
                fail_model.appendRow(item_f)
            
        self.ui.listView_2.setModel(success_model)
        self.ui.listView_3.setModel(fail_model)
        self.log(result)

    def log(self, result):
        global log_name
        log_name = rootdir2 + datetime.datetime.today().strftime('%Y-%m-%d') + '.txt'

        if os.path.exists(log_name):
            write_method = 'a'
        else:
            write_method = 'w'
        
        outfile = open(log_name,write_method)
        
        for item in result:
            outfile.write(item)
        outfile.close()

    def open_log(self):

        if sys.platform == "win32":
            os.startfile(log_name)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            try:
                subprocess.call([opener, log_name])
            except:
                print('whoops')

    def test(self):
        for f in os.walk('/Users/peterhung/Personal Projects/autoFTP/tmp'):
            for item in f[2]:
                if item == '.DS_Store':
                    pass
                else:
                    masterfile_lst.append(item)

        print(masterfile_lst)

    def duplicate_file(self, fp, d):
        copy2(fp,d)

def run():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('/Users/peterhung/Personal Projects/autoFTP/rocketFTP_icon3.png'))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()



        

        

        
        


