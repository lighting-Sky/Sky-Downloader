import re, requests, os
import sys
from hashlib import md5
from concurrent.futures import ThreadPoolExecutor
import  concurrent.futures
from PyQt5.QtCore import pyqtSignal,QEventLoop, QTimer
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QTextCursor

from m3u8UI import Ui_Form
from PyQt5 import QtWidgets
from m3u8 import M3U8
import threading
import shlex,time,shutil
from subprocess import Popen, PIPE
from hashlib import md5

# file_listname = "file-list.txt"
# list_path = "./m3u8/"
file_listname = "file-list.txt"
tmp_path = "tmp/"
global_workers = 8
global_process_data = 0
threadPool = ThreadPoolExecutor(max_workers=global_workers, thread_name_prefix="test_")
class Worker:
    def __init__(self, tasks, workers, task_path, QObject):
        self.task_len = len(tasks)
        self.tasks = tasks
        self.task_path = task_path
        self.QObject = QObject
        self.workers = workers
        self.pool = ThreadPoolExecutor(max_workers = self.workers)
    # def Running(self, func, *args, **kwargs):
    #         # 使用map方法处理任务队列
    #         for i in self.tasks:
    #             results = self.pool.submit(func, i, kwargs)
    #         # # 获取任务的执行结果
            # for result in results:
            #     print(f"Task result: {result}")

class M3u8Parse:
    def __init__(self, url, path, cmd, QObject):
        self.url = url
        self.cmd = cmd
        self.QObject = QObject
        if path:
            self.path = path
        else:
            self.path = "G:/"
        # if self.path != "./":
        #     if not os.path.exists(self.path):
        #         os.makedirs(path)
        #     else:
        #         shutil.rmtree(self.path)
        #         os.mkdir(self.path)
        
                
    def pathCheck(self,path):
        if not os.path.exists(path):
                os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)
    
    def genFileName(self,content):
        obj = md5()
        obj.update(content.encode("utf-8"))
        md5str = obj.hexdigest()
        print(md5str)
        return (md5str)
    
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
    
    
    def MonitorProcess(self):
        print("start Monitor")
        while True:
            file_list = []
            time.sleep(0.1)
            filenames = os.listdir(self.path)
            for file in filenames:
                if os.path.splitext(file)[1] == ".ts":
                    file_list.append(file)
            ts_len = len(file_list)
            print("monitor",ts_len)
            if ts_len >= self.length:
                self.QObject.signal_done.emit(1) 
                break
            else:
                self.QObject.progressBarValue.emit(int(round(ts_len/self.length*100)))

        return file_list
            
            
    def run_command(self, command):
        process = Popen(shlex.split(command), stdout=PIPE)
        st = time.time()
        while True:
            output = process.stdout.readline().rstrip().decode('ANSI')
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

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
        print(self.url)
        print(response.status_code)
        
    def SaveTsVideo(self, url, filename):
        # print (url)
        response = requests.get(url)
        
        with open(self.path+tmp_path+filename, "wb") as f:
            f.write(response.content)
    
    def GetTsFromM3u8(self):
        with open(self.path+'file.m3u8', 'r') as file:
            m3u8_content = file.read()
        
        m3u8_obj = M3U8(m3u8_content)
        self.M3u8Entry = m3u8_obj
        
        media_segments = m3u8_obj.segments
        # 打印媒体段信息

        length = len(media_segments)
        self.length = length
        tasks = []
        filename_index = 0
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"task start!")

        print(f"创建目录:{self.path+tmp_path}")
        self.pathCheck(self.path+tmp_path)
        
        for segment in media_segments:
            filename_index+=1
            ts_url = segment.uri
            url = self.CorrectUrl(ts_url)
            filename = f"{filename_index}.ts"
            # filename = self.genFileName(ts_url)+".ts"
            #file_type = re.findall(r'_(.*?)\?', ts_url)
            with open (self.path+file_listname, "a") as f:
                f.write(f"file '{self.path}{tmp_path}{filename}'\n")
            result = threadPool.submit(self.SaveTsVideo, url, filename)
            tasks.append(result)
            # print(filename)
            # print("result:",result)
        concurrent.futures.wait(tasks) 
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"all-task finish!")
        # self.MergeVideos(global_workers)
        #需要等待所有ts下载完成才开始执行
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"开始合并分片...")
        cmd = f'ffmpeg -loglevel warning -f concat -safe 0 -i {self.path}{file_listname} -map "0:v?" -map "0:a?" -map "0:s?" -c copy -y -bsf:a aac_adtstoasc {self.path}output.mp4'
        print(cmd)
        os.system(self.cmd)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"合并完成！")
        #shutil.rmtree(self.path+tmp_path)
        
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
        # self.run_command(self.cmd)
    

class MyThread(QThread):
    signalForText = pyqtSignal(str)

    def __init__(self,data=None, parent=None):
        super(MyThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.signalForText.emit(str(text))  # 发射信号

    def run(self):
        # 演示代码
        for i in range(5):
            print(i)
            time.sleep(1)
        print("End")

     

class MediaPlayerWin(QtWidgets.QMainWindow, Ui_Form):
    progressBarValue = pyqtSignal(int)  # 更新进度条
    signal_done = pyqtSignal(int)  # 是否结束信号

    def __init__(self):
        super(MediaPlayerWin, self).__init__()
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBarValue.connect(self.updateProBar)
        self.signal_done.connect(self.callback_done)
        self.progressBar.setValue(0)
        self.th = MyThread()
        self.th.signalForText.connect(self.onUpdateText)
        sys.stdout = self.th
        self.StartBtn.setEnabled(False)
    
    def onUpdateText(self,text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def updateProBar(self, i):
        self.progressBar.setValue(i)
    
    def callback_done(self, i):
        self.is_done = i
        if self.is_done == 1:
            self.state_label.setText("完成!")
            ui.progressBar.setValue(100)
    
    def search(self):
        try:
            self.t = MyThread()
            self.t.start()
        except Exception as e:
            raise e

    def startBtnClick(self):
        self.state_label.setText("爬取中...")
        self.progressBar.setValue(0)
        global_workers = self.comboBox.currentText()
        url = self.lineEdit.text()
        pathName = f"{self.PathName.text()}/"
        outName = pathName+self.outPutName.text()
        list_path = pathName
        # print(url)
        #cmd = f"ffmpeg -f concat  -safe 0  -i {list_path}{file_listname} -vcodec copy -acodec copy {outName}.mp4 -y"
        cmd = f'ffmpeg -loglevel warning -f concat -safe 0 -i {pathName}{file_listname} -map "0:v?" -map "0:a?" -map "0:s?" -c copy -y -bsf:a aac_adtstoasc {outName}.mp4'
        
        m3 = M3u8Parse(url, pathName, cmd, self)
        t = threading.Thread(target=m3.Running)
        t.start()
    
    def openPath(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None,"选取文件夹","G:/")
        print(directory)
        self.PathName.setText(directory)
        self.StartBtn.setCheckable(True)
        



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseW = QtWidgets.QMainWindow()
    ui = MediaPlayerWin()
    ui.progressBar.setValue(0)
    ui.setupUi(baseW)
    baseW.show()
    sys.exit(app.exec_())