from .condition import Condition

class LogicExpression():
    def __init__(self, name, arguments = []):
        self.name = name    #and or imply (ecc...)
        self.arguments = arguments
    
    def __str__(self):
        if self.name == "forall" or self.name == "exists":
            if self.name == "imply":
                print(self.name)
                print(str(self.arguments[0]))
                print(str(self.arguments[1]))
            return f"({self.name} (" + " ".join(map(str,self.arguments[0])) + ") " +" ".join(map(str,self.arguments[1])) + ")"
        if self.name == "imply":
            return f"({self.name} {str(self.arguments[0])} {str(self.arguments[1])})"
        return f"({self.name} " + " ".join(map(str,self.arguments)) + ")"
    
    def addCondToArgument(self, argument):
        if self.name == "and":
            self.arguments.append(argument)
        else:
            return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, LogicExpression):
            if self.name == other.name:
                end = True
                for arg in self.arguments:
                    end = end and (arg in other.arguments)
                    if not end: return end
                return end
        if isinstance(other, Condition):
            return False
        return NotImplemented
