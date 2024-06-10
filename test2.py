import subprocess  
  
# 启动 ffmpeg 进程，注意 stderr 被重定向到 PIPE  
popen = subprocess.Popen(  
    'ffmpeg -i "http://devimages.apple.com/iphone/samples/bipbop/gear3/prog_index.m3u8" -y out.mp4',  
    shell=True,  
    stdout=subprocess.PIPE,  
    stderr=subprocess.PIPE,  
    bufsize=1  # 设置行缓冲  
)  
  
# 实时捕获 stderr 输出  
for line in iter(popen.stderr.readline, b''):  
    print("out:", line.decode('utf-8'), end='')  # 解码为 utf-8 并打印  
  
# 等待进程完成  
popen.stderr.close()  
popen.wait()  
  
print('returncode:', popen.returncode)