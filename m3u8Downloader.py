import re, requests, os
import sys
from hashlib import md5

from PyQt5.QtCore import pyqtSignal

from m3u8UI import Ui_Form
from PyQt5 import QtWidgets
from m3u8 import M3U8
import threading
import shlex,time,shutil
from subprocess import Popen, PIPE
import ThreadClass

file_listname = "file-list.txt"
list_path = "./m3u8/"
    

class M3u8Parse:
    def __init__(self, url, path, cmd, QObject):
        self.url = url
        self.cmd = cmd
        self.QObject = QObject
        self.workQueue1 = []
        self.workQueue2 = []
        self.workQueue3 = []
        self.workQueue4 = []
        if path:
            self.path = path
        else:
            self.path = "./"
        if self.path != "./":
            if not os.path.exists(self.path):
                os.makedirs(path)
            else:
                shutil.rmtree(self.path)
                os.mkdir(self.path)
                
    
    def get_dir2file(self):
        file_list =[]
        filenames = os.listdir(self.path)
        for file in filenames:
            if os.path.splitext(file)[1] == ".ts":
                file_list.append(file)
        file_list.sort()
        print(file_list)
        with open (self.path+file_listname, "w") as f:
            for i in file_list:
                f.write(f"file '{i}'\n")
           
    
    def run_command(self, command):
        process = Popen(shlex.split(command), stdout=PIPE)
        st = time.time()
        while True:
            output = process.stdout.readline().rstrip().decode('ANSI')
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

            # if time.time() - st > 3:
            #     os.kill(process.pid, signal.CTRL_C_EVENT)
            #     break
        #self.state_label.setText("完成!")
        rc = process.poll()
        print("rc",rc)
        return rc
    
                
    def requestM3u8(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            with open(self.path+'file.m3u8', 'w') as f:
                f.write(response.text)
            #print(response.text)
        print(response.status_code) 
    
    def GetTsFromM3u8(self):
        with open(self.path+'file.m3u8', 'r') as file:
            m3u8_content = file.read()
        
        m3u8_obj = M3U8(m3u8_content)
        self.M3u8Entry = m3u8_obj
        
        media_segments = m3u8_obj.segments

        # 打印媒体段信息

        length = len(media_segments)
        step = 0
        for segment in media_segments:
            step+=1
            self.QObject.progressBarValue.emit(int(round(step/length*100)))
            #print(segment.uri, segment.duration)
            ts_url = segment.uri
            url = self.CorrectUrl(ts_url)
            filename = re.findall(r'_(.*?)\?', ts_url)
   
            with open (self.path+file_listname, "a") as f:
                f.write(f"file '{filename[0]}'\n")
            response = requests.get(url)
            with open(self.path+filename[0], "wb") as f:
                f.write(response.content)
            #print(filename)
        self.QObject.signal_done.emit(1) 
        
    def CorrectUrl(self, url):
        if url[0:4] !="http":
            UrlTmp = self.url.rsplit("/", 1)
            # print("tmp:",UrlTmp)
            # print (UrlTmp[0]+"/"+url)
            return UrlTmp[0]+"/"+url
        return url

    def Running(self):
        self.requestM3u8()
        self.GetTsFromM3u8()
        self.run_command(self.cmd)
    
    def ParseWork(self):
        t = ThreadClass.MyThread(self.Running)
        t.start()
        

class MediaPlayerWin(QtWidgets.QMainWindow, Ui_Form):
    progressBarValue = pyqtSignal(int)  # 更新进度条
    signal_done = pyqtSignal(int)  # 是否结束信号

    def __init__(self):
        super(MediaPlayerWin, self).__init__()
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(23)
        self.progressBarValue.connect(self.updateProBar)
        self.signal_done.connect(self.callback_done)
    
    def updateProBar(self, i):
        self.progressBar.setValue(i)
    
    def callback_done(self, i):
        self.is_done = i
        if self.is_done == 1:
            self.state_label.setText("完成!")
    
    # 实现pushButton_click()函数，textEdit是我们放上去的文本框的id
    def startBtnClick(self):
        
        url = self.lineEdit.text()
        outName = self.outPutName.text()
        pathName = f"./{self.PathName.text()}/"
        list_path = pathName
        # print(url)
        cmd = f"ffmpeg -f concat  -safe 0  -i {list_path}{file_listname} -vcodec copy -acodec copy {outName}.mp4 -y"
        m3 = M3u8Parse(url, pathName, cmd, self)
        m3.ParseWork()
        # self.signal_done.emit(1) 
        # result = m3.Running()
        # if result == 0:
        #     self.state_label.setText("完成")

        # self.progressBar.setValue(100)
        




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseW = QtWidgets.QMainWindow()
    ui = MediaPlayerWin()
    ui.setupUi(baseW)
    baseW.show()
    sys.exit(app.exec_())