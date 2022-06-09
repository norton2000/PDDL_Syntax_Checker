

class Parameter():
    def __init__(self, name, obj = None):
        self.name = name
        self.obj = obj
    
    def setObject(self, obj):
        self.obj = obj
    
    def __str__(self):
        if self.obj is None:
            return self.name
        return str(self.name)+ " - " + str(self.obj.name)
