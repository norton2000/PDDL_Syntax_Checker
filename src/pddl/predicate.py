

class Predicate():
    def __init__(self, name, arguments = []):
        self.name = name
        self.arguments = arguments              
    
    def addArgument(self, argument):
        self.arguments.append(argument)
    
    def lenArguments(self):
        return len(self.arguments)
    
    def objectArguments(self):
        #Funzione che ritorna gli oggetti del predicato
        return list(map(lambda x: x.obj, self.arguments))
        
    def __str__(self):
        return str(self.name) + " " + " ".join(map(str,self.arguments))
    
    def __eq__(self, other):
        if isinstance(other, Predicate):
            return self.name == other.name and len(self.arguments) == len(other.arguments)
        return NotImplemented
