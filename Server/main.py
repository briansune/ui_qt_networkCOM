# -*- coding: utf-8 -*-

import socket
import serial
import serial.tools.list_ports
import sys
from subprocess import PIPE, Popen
from threading import Thread
import os
import re
import signal

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5 import QtGui
from main_window_ui import Ui_oMainWind


class Window(QMainWindow, Ui_oMainWind):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.sys_ports = []
        self.ui = Ui_oMainWind()
        self.ui.setupUi(self)
        self.connectSignalsSlots()
        self.bStartStopFlag = False
        self.oSocketHolder = None
        self.oSerialHolder = None
        self.oConnectHolder = None
        self.bNormalConnect = False
        self.oProcess = Popen
        self.oQueue = Queue
        self.oThread = Thread

    def connectSignalsSlots(self):
        self.ui.oActInfo.triggered.connect(self.about)
        self.ui.oActExit.triggered.connect(self.close)
        self.ui.oEntryIp0.setText('xxx')
        self.ui.oEntryIp1.setText('xxx')
        self.ui.oEntryIp2.setText('xxx')
        self.ui.oEntryIp3.setText('xxx')
        self.ui.oEntryPort.setText('7000')
        self.updateComList()
        self.ui.oButStartStop.clicked.connect(self.startStopBind)

    def startStopBind(self):
        l_label = ['Stop', 'Start']
        self.bStartStopFlag = not self.bStartStopFlag
        print('The start flag: {}'.format(self.bStartStopFlag))
        self.ui.oButStartStop.setText(l_label[int(not self.bStartStopFlag)])
        if not self.bStartStopFlag:
            self.ui.oListBoxCom.setDisabled(False)
            self.ui.oEntryIp0.setDisabled(True)
            self.ui.oEntryIp1.setDisabled(True)
            self.ui.oEntryIp2.setDisabled(True)
            self.ui.oEntryIp3.setDisabled(True)
            self.ui.oEntryPort.setDisabled(False)
            self.ui.oLbStatus.setPixmap(QtGui.QPixmap(":/red.png"))
            self.closeAll()
        else:
            self.ui.oListBoxCom.setDisabled(True)
            self.ui.oEntryIp0.setDisabled(True)
            self.ui.oEntryIp1.setDisabled(True)
            self.ui.oEntryIp2.setDisabled(True)
            self.ui.oEntryIp3.setDisabled(True)
            self.ui.oEntryPort.setDisabled(True)
            self.ui.oLbStatus.setPixmap(QtGui.QPixmap(":/green.png"))
            self.startTcpIpCom()

    @staticmethod
    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def startTcpIpCom(self):
        o_soc_holder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        o_soc_holder.connect(("8.8.8.8", 80))
        s_my_ip = o_soc_holder.getsockname()[0]
        o_soc_holder.shutdown(socket.SHUT_RDWR)
        o_soc_holder.close()
        print('Site address: {};{}'.format(s_my_ip, self.ui.oEntryPort.text()))
        l_my_ip = str(s_my_ip).split('.')
        self.ui.oEntryIp0.setText(l_my_ip[0])
        self.ui.oEntryIp1.setText(l_my_ip[1])
        self.ui.oEntryIp2.setText(l_my_ip[2])
        self.ui.oEntryIp3.setText(l_my_ip[3])

        print('Com Select: {}'.format(self.ui.oListBoxCom.currentText()))
        print('Port Select: {}'.format(self.ui.oEntryPort.text()))

        self.oProcess = Popen(['com2tcp-rfc2217.bat',
                               str(self.ui.oListBoxCom.currentText()),
                               str(self.ui.oEntryPort.text())], stdout=PIPE, stdin=PIPE)
        self.oQueue = Queue()
        self.oThread = Thread(target=self.enqueue_output, args=(self.oProcess.stdout, self.oQueue))
        self.oThread.daemon = True
        self.oThread.start()

        # read line without blocking
        while True:
            try:
                # line = q.get_nowait()
                line = self.oQueue.get(timeout=.2)
                o_check_normal = re.search('Started TCP', line)
                print(str(line).replace('\n', ''))
                if o_check_normal:
                    self.bNormalConnect = True
            except Empty:
                break

        if not self.bNormalConnect:
            self.startStopBind()

    def closeAll(self):
        os.kill(self.oProcess.pid, signal.CTRL_C_EVENT)
        exit()

    def updateComList(self):
        self.ui.oListBoxCom.clear()
        l_ports = serial.tools.list_ports.comports()
        connected = [element.device for element in l_ports]
        self.ui.oListBoxCom.addItems(connected)

    @staticmethod
    def about():
        o_msg_box = QMessageBox()
        o_msg_box.setWindowTitle("TCP/IP Serial Binding Tool")
        o_msg_box.setText("<p>Designer: Brfo</p>"
                          "<p>Contact: brian.fong@qorvo.com</p>"
                          "<p>Date: 2021</p>")
        o_msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
