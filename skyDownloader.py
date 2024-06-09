import sys,os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox
import time
from dowloaderUi import Ui_Form
from PyQt5 import QtWidgets
import threading

class MediaPlayerWin(QtWidgets.QMainWindow, Ui_Form):

    signal_done = pyqtSignal(int)
        
    # def __init__(self):
    #     super(MediaPlayerWin, self).__init__()
        
    def setupUi(self,Form):
        super(MediaPlayerWin,self).setupUi(Form)
        self.signal_done.connect(self.show5)
        self.lineEdit_path.setText("G:/Download")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        print("setting")
    
    def Running(self):
        self.label_state.setText("爬取中...")
        url = self.lineEdit_url.text()
        pathName = self.lineEdit_path.text()+"/"
        outName = pathName+self.lineEdit_filename.text()
        # print(url)
        #cmd = f"ffmpeg -f concat  -safe 0  -i {list_path}{file_listname} -vcodec copy -acodec copy {outName}.mp4 -y"
        
        cmd = f'ffmpeg -threads 0  -i "{url}" -c copy -y -bsf:a aac_adtstoasc {outName}.mp4'
        print(cmd)
        os.system(cmd)
        # time.sleep(5)
        self.signal_done.emit(1)

    def show5(self):
        msgBox = QMessageBox()
        msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msgBox.information(self,"任务提示","爬取完成!")
        # msgBox.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        # msgBox.setWindowFlags(msgBox.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        # print(reply)
        # msgBox.show()
        self.label_state.setText("")
    def startDownload(self):
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



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseW = QtWidgets.QMainWindow()
    ui = MediaPlayerWin()
    print("1")
    ui.setupUi(baseW)
    print("2")
    baseW.show()
    sys.exit(app.exec_())