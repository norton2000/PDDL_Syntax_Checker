

class Action():
    def __init__(self, name, parameters = [], precondition = [], effect = []):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect
    
    def addParameters(self, argument):
        self.parameters.append(argument)
    
    def addPrecondition(self, argument):
        self.preconditions.append(argument)
    
    def addEffect(self, argument):
        self.effects.append(argument)
    
    def __str__(self):
        return "Action "+self.name+":\nParameters: "+", ".join(map(str,self.parameters))+"\nPrecondition: "+str(self.precondition)+"\nEffect: "+str(self.effect)
    
    def __eq__(self, other):
        if isinstance(other, Action):
            return self.name == other.name
        return NotImplemented
