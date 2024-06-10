from Task import Task

class DownloadList:
    task_list = []
    workingId = 0
        
    def addTask(self, task):
        self.task_list.append(task)
    
    def updateTaskProgress(self,taskId):
        self.task_list[taskId].per="已完成"
    
    def checkListEmpty(self):
        if len(self.task_list) == 0:
            return True
        return False
    
    def getTaskRunning(self):
        if self.IsWorkFinish():
            return
        workId = self.workingId
        self.workingId+=1
        return self.task_list[workId]
    
    def IsWorkFinish(self):
        if self.workingId >=len(self.task_list):
            return True
        return False
