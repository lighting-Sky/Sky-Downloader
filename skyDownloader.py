import sys,os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QListView, QTableWidgetItem
import time
from dowloaderUi import Ui_Form
from PyQt5 import QtWidgets
import threading
import shlex
from subprocess import Popen, PIPE
import re
import threading  
from Task import Task
from MyThread import MyThread
from DdList import DownloadList

gid = 0

def convert_time_to_seconds(time_str):  
    parts = time_str.split(':')  
    if len(parts) == 3:  
        hours, minutes, seconds = map(int, parts)  
        total_seconds = hours * 3600 + minutes * 60 + seconds  
        return total_seconds  
    else:  
        return 0
    
class MediaPlayerWin(QtWidgets.QMainWindow, Ui_Form):

    outPutLogText = ""
    signal_done = pyqtSignal(int)
    tasks = DownloadList()
    # def __init__(self):
    #     super(MediaPlayerWin, self).__init__()
        
    def setupUi(self,Form):
        super(MediaPlayerWin,self).setupUi(Form)
        self.pushButton_download.setEnabled(True)
        self.signal_done.connect(self.TaskDoneDisplay)
        self.lineEdit_path.setText("G:/Download")
        self.progressBar.setValue(0)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.slm = QStandardItemModel()
        head_label = ["文件名","路径","url地址","进度"]
        self.slm.setHorizontalHeaderLabels(head_label)
        self.tableView.setModel(self.slm)
        
        self.pushButton_choose.clicked.connect(self.choosePath) # type: ignore
        self.pushButton_download.clicked.connect(self.startDownload) # type: ignore
        self.pushButton_exit.clicked.connect(self.exitApp) # type: ignore
        self.pushButton.clicked.connect(self.addTask) # type: ignore
    
    def updateProgressValue(self):
        # with lock:
        if self.outPutLogText == "":
            self.label_state.setText(f"")
            return
        dulation = re.findall(r"Duration: (\d{2}:\d{2}:\d{2})", self.outPutLogText)
        current_du = re.findall(r'time=(\d{2}:\d{2}:\d{2})', self.outPutLogText)
        speed = re.findall(r'bitrate=([0-9a-z./]+)', self.outPutLogText)
        
        speed = speed[-1] if speed else "0kbit/s"
        dulation = dulation[0] if dulation else "00:00:00"
        current_du = current_du[-1] if current_du else "00:00:00"
        
        dulation_sec = convert_time_to_seconds(dulation)
        current_du_sec = convert_time_to_seconds(current_du)
        if dulation_sec == 0:
            per = 0
        elif dulation_sec <=current_du_sec:
            per = 100
            self.outPutLogText = ""
        else:
            per = int((current_du_sec/dulation_sec)*100//1)
        
        self.label_state.setText(f"总时长:{dulation} 已下载: {current_du} 速率:{speed}")
        self.progressBar.setValue(per)
        
    def timerClick(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressValue)
        self.timer.start(1000)
    
    def Running(self):
        while True:
            task = self.tasks.getTaskRunning() if not self.tasks.checkListEmpty() else None
            if task:
                print(task)
                self.label_state.setText("爬取中...")
                self.slm.setItem(task.id,3,QStandardItem("爬取中"))
                # url = self.lineEdit_url.text()
                # pathName = self.lineEdit_path.text()+"/"
                # outName = pathName+self.lineEdit_filename.text()
                cmd = f'ffmpeg  -threads 0  -i "{task.url}" -c copy -y -bsf:a aac_adtstoasc {task.path}{task.title}.mp4'
                print(time.localtime(), cmd)
                p = Popen(cmd, shell = True,
                                stdout = PIPE,
                                stderr = PIPE) 
                # 获取实时输出并处理
                for line in iter(p.stderr.readline, b''):  
                    print("out:", line.decode('utf-8'), end='')  # 解码为 utf-8 并打印  
                    self.outPutLogText+=line.decode('utf-8')
                # 等待进程完成  
                p.stderr.close()  
                p.wait()  
                self.signal_done.emit(1)
                self.label_state.setText("下载完成！")
                self.slm.setItem(task.id, 3, QStandardItem("已完成"))
            else:
                # print("列表空，等待中。。。")
                time.sleep(1)

    def TaskDoneDisplay(self):
        msgBox = QMessageBox()
        msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msgBox.information(self,"任务提示","爬取完成!")
        self.label_state.setText("")
        self.outPutLogText = ""
        self.progressBar.setValue(0)
        
    def startDownload(self):
        self.timerClick()
        t = threading.Thread(target=self.Running)
        t.start()
        
    
    def choosePath(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹","G:/")
        print(directory)
        self.lineEdit_path.setText(directory)
        self.pushButton_download.setEnabled(True)
        
    def exitApp(self):
        reply = QMessageBox.question(self, '退出', '确定退出？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            print('退出')
            sys.exit(app.exec_())
        else:
            print('不退出')
    
    def addTask(self):
        global gid
        url = self.lineEdit_url.text()
        pathName = self.lineEdit_path.text()+"/"
        outName = self.lineEdit_filename.text()
        if not outName or not pathName or not url:
            QMessageBox.information(self,"提示","不能添加空值!")
            return
        t = Task(gid, outName,pathName,url,"未开始")
        self.slm.appendRow(t.convert2QStandardItems())
        self.tasks.addTask(t)
        gid+=1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseW = QtWidgets.QMainWindow()
    ui = MediaPlayerWin()
    ui.setupUi(baseW)
    baseW.show()
    sys.exit(app.exec_())