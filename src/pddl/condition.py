

class Condition():
    def __init__(self, name, arguments = [], positive=True):
        self.name = name
        self.arguments = arguments
        self.positive=positive
        
    def addArgument(self, argument):
        self.arguments.append(argument)
        
    def lenArguments(self):
        return len(self.arguments)
        
    def __str__(self):
        ante = "" if self.positive else "(not "
        post = "" if self.positive else ")"
        return ante + "("  + self.name + " " +" ".join(map(str,self.arguments)) + ")" + post
    
    def isOpposite(self, other):
        if isinstance(other, Condition):
            return self.name == other.name and self.positive != other.positive
        return False
    
    def __eq__(self, other):
        if isinstance(other, Condition):
            return self.name == other.name and self.positive == other.positive
        return NotImplemented
