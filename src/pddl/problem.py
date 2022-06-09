

class Problem():
    def __init__(self, domain = None):
        self.name = None
        self.domain = domain
        self.objects = None
        self.init = []
        self.goal = None

    def setObjects(self, objs):
        self.objects = objs
    
    def findObject(self, name):
        return next((x for x in self.objects if x.name == name), None)      
    
    def addCondition(self,cond):
        self.init.append(cond)
    
    def setGoal(self, goal):
        self.goal = goal

    def __str__(self):
        return f"Problem: {self.name}\nObjects: "+"; ".join(map(str,self.objects))+"\n\nInit:\n"+"\n".join(map(str,self.init))+"\n\nGoal:\n"+str(self.goal)
