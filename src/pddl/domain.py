

class Domain():
    def __init__(self):
        self.name = None
        self.predicates = []
        self.actions = []
        self.requirements = []
        self.typing = False
        self.objects = None
    
    def addPredicate(self, predicate):
        self.predicates.append(predicate)
    
    def addAction(self, action):
        self.actions.append(action)
    
    def deleteAction(self, action):
        self.actions.remove(action)
        
    def addRequirement(self, req):
        self.requirements.append(req)

    def checkPredicate(self, name, length):
        predicate = findPredicate(name)
        return predicate and predicate.lenArguments()==length
    
    def findPredicate(self, name):
        return next((x for x in self.predicates if x.name == name), None)
    
    def findAction(self,name):
        return next((x for x in self.actions if x.name == name), None)
    
    def activeTyping(self):
        self.typing = True
        self.objects = []
    
    def addObject(self, obj):
        self.objects.append(obj)
    
    def deleteObject(self, obj):
        self.objects.remove(obj)
    
    def getObject(self, name):  #funzione che ritorna l'oggetto presente nel dominio ricercato tramite il nome. Ritorna None se il nome dell'oggetto non esiste nel dominio.
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
        
    def __str__(self):
        return f"Domain: {self.name}\n\nPredicates: "+"; ".join(map(str,self.predicates))+"\n\nActions:\n"+"\n\n".join(map(str,self.actions))
