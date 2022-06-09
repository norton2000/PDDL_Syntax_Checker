

class Object():
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        
    def __str__(self):
        if self.parent==None:
            return self.name
        return str(self.name) + " - " + str(self.parent.name)
    
    def __eq__(self, other):
        if isinstance(other, Object):
            return self.name == other.name
        return NotImplemented
