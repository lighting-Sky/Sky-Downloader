#encoding:utf-8  # 在 Python 3 中不是必需的，但通常不会有问题  
import threading  
from concurrent.futures import ThreadPoolExecutor  
import concurrent.futures
import random  
import time  
  
# 创建一个包含2条线程的线程池  
# pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="test_")  # 定义两个线程  
  
def task(name, i):  
    sleep_seconds = random.randint(1, 3)    # 随机睡眠时间  
    print('线程名称：%s，参数：%s，睡眠时间：%s' % (threading.current_thread().name, i, sleep_seconds))  
    time.sleep(sleep_seconds)   # 定义睡眠时间  
  
def func():  
    print("start")  
    pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="test_")  # 定义两个线程 
    futures =[]
    for i in range(10):  # 为了简化示例，我们只提交10个任务  
        future = pool.submit(task, "任务名", i)  # 提交 task 函数到线程池  
        futures.append(future)
    # 注意：在真实情况下，你可能需要等待所有任务完成，但这里为了简化示例，我们不会等待  
    concurrent.futures.wait(futures) 
    print("test")
  
if __name__ == '__main__':  
    t = threading.Thread(target=func)  
    t.start()  
    t.join()  # 等待主线程完成