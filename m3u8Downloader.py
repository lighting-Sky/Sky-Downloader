import re, requests, os
import sys
from hashlib import md5
from concurrent.futures import ThreadPoolExecutor
import  concurrent.futures
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
global_workers = 16
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
    
    
    def MonitorProcess(self):
        print("start Monitor")
        while True:
            file_list = []
            filenames = os.listdir(self.path)
            for file in filenames:
                if os.path.splitext(file)[1] == ".ts":
                    file_list.append(file)
            ts_len = len(file_list)
            if ts_len >= self.length:
                self.QObject.signal_done.emit(1) 
                break
            else:
                self.QObject.progressBarValue.emit(int(round(ts_len/self.length*100)))

        return file_list
            
    # def Merge2mp4(self, file1, file2):
    #     cmd1 = f"ffmpeg -i {file1} -qscale 4 tmp1.mpg"
    #     cmd2 = f"ffmpeg -i {file2} -qscale 4 tmp2.mpg"
    #     return new_file
    
    # def MergeVideos(self, workers):
    #     #将文件分成N分
    #     with open(self.path+file_listname, "r") as f:
    #         lines = f.readlines()
    #         lens = len(lines)
    #         worker_one_task = (lens+(workers//2))//workers
    #         start = 1
    #         for i in range(1, lens+1):
    #             if i <= workers*worker_one_task and i >= start* worker_one_task:
    #                 start+=1
    #             with open(self.path+f"{start}.txt", "a") as f:
    #                 f.write(lines[i-1])
    #     threadPool = ThreadPoolExecutor(max_workers=global_workers, thread_name_prefix="test_")
        # tasks = []
        # for i in range(1, workers+1):
        #     cmd = f"ffmpeg -f concat  -safe 0  -i {self.path}{i}.txt -vcodec copy -acodec copy {self.path}{i}.mp4 -y"
        #     result = threadPool.submit(self.run_command, cmd)
        #     tasks.append(result)
        # concurrent.futures.wait(tasks)
        # for i in range(1, workers+1):
        #     resultName = "result.mp4"
        #     cmd1 = f"ffmpeg -i {resultName} -qscale 4 tmp1.mpg"
        #     cmd = f"ffmpeg -f concat  -safe 0  -i {self.path}{i}.txt -vcodec copy -acodec copy {self.path}{resultName} -y"

            
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
        with open(self.path+filename, "wb") as f:
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

        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"task start!")

        for segment in media_segments:
            ts_url = segment.uri
            url = self.CorrectUrl(ts_url)
            filename = re.findall(r'_(.*?)\?', ts_url)
            with open (self.path+file_listname, "a") as f:
                f.write(f"file '{filename[0]}'\n")
            result = threadPool.submit(self.SaveTsVideo, url, filename[0])
            tasks.append(result)
            # print(filename)
            # print("result:",result)
        concurrent.futures.wait(tasks) 
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"all-task finish!")
        # self.MergeVideos(global_workers)
        #需要等待所有ts下载完成才开始执行
        cmd = f'ffmpeg -loglevel warning -f concat -safe 0 -i {list_path}{file_listname} -map "0:v?" -map "0:a?" -map "0:s?" -c copy -y -bsf:a aac_adtstoasc test.mp4'
        os.system(cmd)
        
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
    
    def updateProBar(self, i):
        self.progressBar.setValue(i)
    
    def callback_done(self, i):
        self.is_done = i
        if self.is_done == 1:
            self.state_label.setText("完成!")
            ui.progressBar.setValue(100)
    
    # 实现pushButton_click()函数，textEdit是我们放上去的文本框的id
    def startBtnClick(self):
        self.state_label.setText("爬取中...")
        self.progressBar.setValue(0)
        global_workers = self.comboBox.currentText()
        url = self.lineEdit.text()
        outName = self.outPutName.text()
        pathName = f"./{self.PathName.text()}/"
        list_path = pathName
        # print(url)
        cmd = f"ffmpeg -f concat  -safe 0  -i {list_path}{file_listname} -vcodec copy -acodec copy {outName}.mp4 -y"
        m3 = M3u8Parse(url, pathName, cmd, self)
        t = threading.Thread(target=self.Running)
        t.start()

        # self.signal_done.emit(1) 
        # result = m3.Running()
        # if result == 0:
        #     self.state_label.setText("完成")

        # self.progressBar.setValue(100)
        




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    baseW = QtWidgets.QMainWindow()
    ui = MediaPlayerWin()
    ui.progressBar.setValue(0)
    ui.setupUi(baseW)
    baseW.show()
    sys.exit(app.exec_())