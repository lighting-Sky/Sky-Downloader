from PyQt5.QtGui import QStandardItem
class Task:
    def __init__(self, id, title,path, url, per):
        self.id = id
        self.url=url
        self.title=title
        self.per = per
        self.path = path
        
    def convert2QStandardItems(self):
        qitemRow = [
            QStandardItem(self.title),
            QStandardItem(self.path),
            QStandardItem(self.url),
            QStandardItem(self.per)
        ]
    
        return qitemRow