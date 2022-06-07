__all__ = ["ParseError", "parse_nested_list"]
import os

SUPPORTED_REQUIREMENTS = ["typing", "strips", "adl", "negative-preconditions"]
SUPPORTED_CONDITION = ["not", "forall"]


class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value
        
class SynError(Exception):
    def __init__(self, text, line, word):
        self.line = line
        self.word = word
        self.text = text
    def __str__(self):
        return self.text

class SupportException(Exception):
    def __init__(self, text, line, word):
        self.line = line
        self.word = word
        self.text = text
    def __str__(self):
        return self.text

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
    
    def activeTyping(self):
        self.typing = True
        self.objects = []
    
    def addObject(self, obj):
        self.objects.append(obj)
        
    def getObject(self, name):  #funzione che ritorna l'oggetto presente nel dominio ricercato tramite il nome. Ritorna None se il nome dell'oggetto non esiste nel dominio.
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
        
    def __str__(self):
        return f"Domain: {self.name}\n\nPredicates: "+"; ".join(map(str,self.predicates))+"\n\nActions:\n"+"\n\n".join(map(str,self.actions))

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

#Parameters is a list of string, precondtion and effect a list of Condition
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

def addCondToExpr(expr, cond):
    #Funzione che aggiunge una condizione a qualsiasi espressione
    if isinstance(expr, LogicExpression):
        expr.addCondToArgument(cond)
        return expr
    if isinstance(expr, Condition): #Se l'espressione è una condizione allora la fa diventare un espressione logica con and e con entrambe le condizioni
        return LogicExpression("and", [expr, cond])
    return NotImplemented   #Se non è ne una Condition ne una LogicExpression c'è qualcosa che non va, non è stato implementato per questo
        
#Function that take an expected expression and the expression and check that they are equal, if not they ryse an SynError.
def expect(expected, current_token, err=True):
    if type(current_token) == list:
        return expect(expected, current_token[0], err)
    (word, n_line) = current_token
    if not word == expected:
        if err:
            raise SynError(f'Expected "{expected}" but we have "{word}".', n_line, word)
        return False
    return True
    
def expectStarting(expected, current_token):
    (word, n_line) = current_token
    if not word[:len(expected)] == expected:
        raise SynError(f'Expected a "{expected}" before "{word}".', n_line, word)

def checkName(lista, subject="domain"):
    #subject è o domain o problem a seconda di quale nome si sta facendo il check
    expect(subject,lista[0])
    if len(lista) > 2:
        (word, n_line) = lista[2]
        raise SynError(f'The {subject} name must consist of only one word, find "{word}".', n_line, word)
    return lista[1][0]
    
def checkDomainName(lista):
    expect("domain",lista[0])
    domain.name = lista[1][0]
    if len(lista) > 2:
        (word, n_line) = lista[2]
        raise SynError(f'The domain name must consist of only one word, find "{word}".', n_line, word)

def checkRequirements(lista):
    expect(":requirements",lista[0])
    for (req,n_line) in lista[1:]:
        expectStarting(":",(req,n_line))
        if req[1:] not in SUPPORTED_REQUIREMENTS:
            raise SupportException(f"requirement {req[1:]} is not supported.",n_line,req)
            return
        if req[1:] == "typing" or req[1:] == "adl":
            domain.activeTyping();
        domain.addRequirement(req)

def addObjects(objsName,parent=None):
    for objName in objsName:
        obj = Object(objName,parent)
        domain.addObject(obj)

def checkTypesObjects(lista):
    expect(":types",lista[0])
    waitingTypeFather = []
    i = 1
    while i<len(lista):
        (name,n_line) = lista[i]
        if name == "-": #Allora l'elemento successivo sarà l'oggetto genitore di tutti quelli precedenti. 
            i+=1
            (name,n_line) = lista[i]    
            parObj = domain.getObject(name)  
            if not parObj:  #Controllo che effettivamente esiste l'oggetto gentiore altrimenti lo creo
                parObj = Object(name)
                domain.addObject(parObj)
            addObjects(waitingTypeFather,parObj)    #Tutta la lista di oggetti che era in attesa di genitore ora posso crearli
            waitingTypeFather = []
        else:       #Nuovo oggetto
            if name in waitingTypeFather or domain.getObject(name):     #Controllo se ho già un oggetto con questo nome
                raise SynError(f'type "{name}" already exist.', n_line, name)
            waitingTypeFather.append(name)  #Inserisco nella lista degli oggetti da creare
        i+=1
    addObjects(waitingTypeFather)   #Creo gli oggetti che non hanno genitori
        
def checkVariableList(lista):
    for elem in lista:
        expectStarting("?",elem)

def checkPredicates(lista):
    expect(":predicates",lista[0])
    for predicate in lista[1:]:
        checkSinglePredicate(predicate)

def addVariables(variables, newVariablesName, typ=None):
    for name in newVariablesName:
        variables.append(Parameter(name,typ))

def checkVariables(lista, variable=True):
    variables = []
    waitingType = []
    i = 0
    while i<len(lista):
        (elem,n_line) = lista[i]
        if elem == "-": #Allora l'elemento successivo sarà l'oggetto di tutti i parametri precedenti. 
            i+=1
            (elem,n_line) = lista[i]    
            typ = domain.getObject(elem) 
            if not typ:  #Controllo che effettivamente esiste l'oggetto gentiore
                raise SynError(f'types "{elem}" doesn\'t exist.', n_line, elem)
            addVariables(variables,waitingType,typ)    #Inserisce le variabili in waitingType di tipo typ all'interno della lista variables
            waitingType = []
        else:
            if variable:
                expectStarting("?",lista[i])
            waitingType.append(elem)
        i+=1
    addVariables(variables,waitingType)
    return variables
    
def checkSinglePredicate(pred):
    name = pred[0][0]
    variables = checkVariables(pred[1:])
    predicate = Predicate(name,variables)
    domain.addPredicate(predicate)

def analyzePredInCond(name, params, n_line, parameters, nameAction):
    predicate = domain.findPredicate(name)
    if not predicate:
        raise SynError(f'The predicate "{name}" does not exist in action {nameAction}.', n_line, name)
    if not predicate.lenArguments()==len(params):
        raise SynError(f'Predicate "{name}" must have {predicate.lenArguments()} arguments, find {len(params)} arguments in action {nameAction}.', n_line, name)
    for param in params:
        if param[0] not in parameters:
            raise SynError(f'Parameters "{param[0]}" does not exist in action {nameAction}.', param[1], param[0])

def computeLogicExpression(lista,parameters,nameAction,notAllowed = [],currNotAllowed = []):
    (exp,n_line) = lista[0]
    
    if exp in notAllowed or exp in currNotAllowed:
        raise SynError(f'You cannot use the expression "{exp}" here', n_line, exp)
    
    if exp == "and" or exp == "or":
        arguments = computeListLogicExpression(lista[1:],parameters,nameAction,notAllowed,currNotAllowed=[exp]) #Dopo un and non ci può essere un altro and (Stessa cosa con or)
        return LogicExpression(exp, arguments)
    elif exp == "imply":   #Imply work in progress
        arguments1 = analyzeCond(lista[1],parameters,nameAction,notAllowed)
        arguments2 = analyzeCond(lista[2],parameters,nameAction,notAllowed)
        return LogicExpression(exp, (arguments1,arguments2))
    elif exp == "forall" or exp == "exists":
        variables = checkVariables(lista[1])
        newparameters = list(map(lambda elem: elem.name,variables))
        if set(newparameters).intersection(parameters):         #Controlla se stai usando dei parametri già usati
            commonParameter = set(newparameters).intersection(parameters).pop()
            raise SynError(f"You shouldn't use the same variable in a forall or exists clause as you have in the parameters. Check {commonParameter}", n_line, commonParameter)
        if lista[2][0][0] == "when":
            arguments = computeListLogicExpression(lista[2][1:],parameters+newparameters,nameAction,notAllowed)
            return LogicExpression(exp, (variables,[LogicExpression("when",arguments)]))
        arguments = computeListLogicExpression(lista[2:],parameters+newparameters,nameAction,notAllowed)
        return LogicExpression(exp, (variables,arguments))
    else:
        return analyzeSingleCond(lista,parameters,nameAction)

def computeListLogicExpression(lista,parameters,nameAction,notAllowed = [],currNotAllowed = []):
    result = []
    for elem in lista:
        result.append(computeLogicExpression(elem,parameters,nameAction,notAllowed,currNotAllowed))
    return result
    
def analyzeSingleCond(elem,parameters,nameAction):
    positive = elem[0][0] != "not"      #False if the sentence is a negation
    if not positive:
        elem = elem[1]
    name = elem[0][0]
    analyzePredInCond(name, elem[1:], elem[0][1], parameters,nameAction)
    arguments = list(map(lambda e: e[0],elem[1:]))
    return Condition(name, arguments, positive)

def analyzeCond(lista, parameters,nameAction,notAllowed = []):
    return computeLogicExpression(lista,parameters,nameAction,notAllowed)
        
def checkAction(action):
    expect(":action",action[0])
    name = action[1][0]
    expect(":parameters",action[2])
    variables = checkVariables(action[3])
    #checkVariableList(action[3])
    parameters = list(map(lambda elem: elem.name,variables))
    expect(":precondition",action[4])
    prec = analyzeCond(action[5],parameters,name)
    expect(":effect",action[6])
    eff = analyzeCond(action[7],parameters,name,notAllowed=["or"])
    action = Action(name, variables, prec, eff)
    domain.addAction(action)

#Function that take the input and return a list of a tuple of all the word with the correspective line.
def tokenize(input):
    for count_line, line in enumerate(input):
        line = line.split(";", 1)[0]  # Strip comments.

        try:
            line.encode("ascii")
        except UnicodeEncodeError:
            raise ParseError("Non-ASCII character outside comment: %s" %
                             line[0:-1])
        line = line.replace("(", " ( ").replace(")", " ) ").replace("?", " ?")
        for token in line.split():
            yield (token.lower(), count_line)

#Function that ricursive check each word. Each parenthesis will become a sublist
def parse_list_aux(tokenstream):
    # Leading "(" has already been swallowed.
    while True:
        try:
            (token, n_line) = next(tokenstream)
        except StopIteration:
            raise ParseError("Missing ')', check all parenthesis")
        if token == ")":
            return
        elif token == "(":
            yield list(parse_list_aux(tokenstream))
        else:
            yield (token,n_line)

#MAIN
fileName = os.getcwd() + "\\Examples\\pddlEditordomain1.pddl"
fileName = os.getcwd() + "\\Examples\\domain.pddl"
domain = Domain()
try:
    input_file = open(fileName, "r").readlines()
    tokens = tokenize(input_file)
    next_token = next(tokens)
    if next_token[0] != "(":
        raise ParseError("Expected '(' at the beginning, got '%s'." % next_token[0])
    result = list(parse_list_aux(tokens))
    for tok in tokens:  # Check that generator is exhausted.
        raise ParseError("Unexpected token: %s." % tok)
    #print(result)
    i=0
    expect("define",result[i])  #define domain
    i += 1
    domain.name = checkName(result[i],"domain")  #Domain name
    i += 1
    if(expect(":requirements",result[i],False)):
        checkRequirements(result[i])
        i += 1
    if domain.typing and expect(":types",result[i],False):
        checkTypesObjects(result[i])
        i += 1
    checkPredicates(result[i])  #Check Predicates
    i += 1
    #for predicate in domain.predicates:
        #print(predicate)
    print()
    while i<len(result):
        checkAction(result[i])
        i += 1

    #for action in domain.actions:
        #print(action)
        #print()
        #print(action.precondition[0])
    print(domain)
    print()

except ParseError as err:
    print(err)
except (SynError,SupportException) as err:
    line = err.line
    word = err.word
    print(f'  File "\domain.pddl", line {line+1}')
    print(f"    {input_file[line][:-1]}")
    pos = input_file[line].find(word)
    if pos != -1:
        print(" " * (pos+4) + "^")
    print(f'SyntaxPddlError: {err}')

print()

#------------------------------------------------------------------------------------
#PROBLEM
#------------------------------------------------------------------------------------

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

def checkProblemDomain(lista):
    expect(":domain",lista[0])
    if len(lista) > 2:
        (word, n_line) = lista[2]
        raise SynError(f'The domain name must consist of only one word, find "{word}".', n_line, word)
    if lista[1][0] != domain.name:
        (word, n_line) = lista[1]
        raise SynError(f'The domain "{word}" is unknown. Maybe you meant "{domain.name}"', n_line, word)
    #Se si deve assegnare il dominio al problema qui, ora lo faccio all'inizio quando creo oggetto problem

def checkObjects(lista):
    expect(":objects",lista[0])
    variables = checkVariables(lista[1:],False) #False perché non sono variabili ma oggetti quindi non iniziano con ?
    #parameters = list(map(lambda elem: elem.name,variables))
    problem.setObjects(variables)

def checkTypingBetweenObject(parent, child):    #Dati tue type controlla se child è == a father oppure father è presente tra i parent dei parent di child
    if child == None:       #Caso base, non ho trovato il tipo "parent" tra i parent di child
        return False
    return child==parent or checkTypingBetweenObject(parent, child.parent)  #Passo ricorsivo

def checkSingleProblemCondition(cond):
    (word, n_line) = cond[0]
    pred = domain.findPredicate(word)   #findPredicate ritorna Null se non ha trovato il predicato con quel nome
    if not pred:                        #Se pred è Null allora lancia Synerror
        raise SynError(f'The predicate "{word}" Does not exist in the current domain "{domain.name}"', n_line, word)
    if pred.lenArguments() != len(cond[1:]):
        raise SynError(f'The predicate "{word}" wants {pred.lenArguments()} arguments. {len(cond[1:])} were found.', n_line, word)
    i = 1
    objs = []
    for typeRequest in pred.objectArguments():
        obj = problem.findObject(cond[i][0])
        if not obj:
            raise SynError(f'The object {cond[i][0]} Does not exist in the current problem.', n_line, cond[i][0])
        if(domain.typing):
            typeReal = obj.obj
            if not checkTypingBetweenObject(typeRequest,typeReal):
                raise SynError(f'The object {cond[i][0]} is of the type {typeReal.name}, whereas the predicate {word} wants as its {i} object the type {objRequest.name}.', n_line, cond[i][0])
        objs.append(obj)
        i+=1
    #Uso il nome per creare un nuovo predicato perché quello che ho nel dominio non ha collegato gli oggetti giusti
    return Predicate(word,objs)
    
def checkInit(lista):
    expect(":init",lista[0])
    for elem in lista[1:]:
        initCond = checkSingleProblemCondition(elem)
        problem.addCondition(initCond)
    
def checkGoal(lista):
    expect(":goal",lista[0])
    parameters = list(map(lambda elem: elem.name,problem.objects))
    goal = analyzeCond(lista[1],parameters,"Goal")
    problem.setGoal(goal)
    
fileNamePr = os.getcwd() + "\\Examples\\pddlEditorproblem1.pddl"
fileNamePr = os.getcwd() + "\\Examples\\problem.pddl"
problem = Problem(domain)
try:
    input_filePr = open(fileNamePr, "r").readlines()
    tokens = tokenize(input_filePr)
    next_token = next(tokens)
    if next_token[0] != "(":
        raise ParseError("Expected '(' at the beginning, got '%s'." % next_token[0])
    result = list(parse_list_aux(tokens))
    for tok in tokens:  # Check that generator is exhausted.
        raise ParseError("Unexpected token: %s." % tok)
    i=0
    expect("define",result[i])  #define problem
    i += 1
    problem.name = checkName(result[i],"problem")  #Problem name
    i += 1
    checkProblemDomain(result[i])
    i += 1
    checkObjects(result[i])
    i += 1
    checkInit(result[i])
    i += 1
    checkGoal(result[i])
    print(problem)

except ParseError as err:
    print(err)
except (SynError,SupportException) as err:
    line = err.line
    word = err.word
    print(f'  File "\problem.pddl", line {line+1}')
    print(f"    {input_filePr[line][:-1]}")
    pos = input_filePr[line].find(word)
    if pos != -1:
        print(" " * (pos+4) + "^")
    print(f'SyntaxPddlError: {err}')
    

## OPTIMIZING AUXILIARY FUNCTIONS

def condInExp(cond, exp):
    #Data una condizione e un espressione, ritorna True se quella condizione compare nell'espressione
    if isinstance(exp, Condition):
        return cond == exp
    exist = False
    for c in exp.arguments:
        exist = exist or condInExp(cond,c)
        if exist: return exist
    return exist

def allCondinExp(exp):
#Dato un espressione logica ritorna tutte e solo le condizioni all'interno dell'espressione
    if isinstance(exp, Condition):
        return [exp]
    if not isinstance(exp, LogicExpression):    #Se non è una LogicExpression e nemmeno un Condition vuol dire che sono parametri da non ritornare
        return []
    conds = []
    for cond in exp.arguments:
        if isinstance(cond, list) or isinstance(cond, tuple):
            for cond_part in cond:
                conds += allCondinExp(cond_part)
        else:
            conds += allCondinExp(cond)
    return conds

def computeParametersInExpr(logicExpr):
    allParam = set({})       #Un set
    for cond in allCondinExp(logicExpr):
        params = cond.arguments
        for elem in params:
            if not elem in allParam:
                allParam.add(elem)
    return allParam

def computeDifferenceInParametersName(expr1, expr2):
    #Ritorna un Dizionario che ha come chiavi i nomi dei parametri di expr2 che non sono in expr1
    #ma che corrispondono a parametri di expr1, questi parametri di expr1 sono gli argomenti di quelle chiavi
    
    #Ancora non si tiene traccia di se ho più condizioni dello stesso tipo (tipo room ?from e room ?to)
    conds1 = allCondinExp(expr1)
    conds2 = allCondinExp(expr2)
    paramname2namefinal = {}    #Inizializza il dizionario
    for cond in conds1:         #Per ogni condizione in conds1
        if cond in conds2:      #Se questa condizione sta in conds2 (ci deve stare per forza se si uniscono le azioni)
            index = conds2.index(cond)
            cond2 = conds2[index]       #Prendi la corrispettiava azione in conds2
            params = cond.arguments
            params2 = cond2.arguments
            if len(params)!=len(params2):
                print("ERROR, i parametri non corrispondono!")  #Temp
            if params != params2:       #Se i paramtri dei due sono diversi allora bisogna inserirli nel dizionario
                for i, param in enumerate(params):
                    if params2[i]!=param and not params2[i] in paramname2namefinal.keys():  #Se è diverso e non è già nel dizionario
                        paramname2namefinal[params2[i]] = param     #Inserisci nel dizionario la coppia param2-param
        else:
            print("ERROR, Stai calcolando differenza ma qualcosa non quadra!")  #Temp
    return paramname2namefinal

def changeParameters2Expr(expr, namepre2namepost):
    #Cambia il nome di tutti i parametri nell'espressione logica se presenti nel dizionario, ritorna tutti i parametri non presenti
    output = []
    for cond in allCondinExp(expr):
        for i, par in enumerate(cond.arguments):
            if par in namepre2namepost.keys():
                cond.arguments[i] = namepre2namepost[par]
            else:
                output.append(cond.arguments[i])
    return output

def effectUnion(effect1, effect2):
    #Unisce tutte le condizioni di tutti gli effetti.   (Tiene conto solo se sono tutti and)
    output = effect2                #sicuro contiene tutte gli effetti della seconda azione
    conds1 = allCondinExp(effect1)
    conds2 = allCondinExp(effect2)   
    for cond1 in conds1:        #Per ogni condizione degli effetti della prima azione
        if cond1 not in conds2: #Se la condizione non è presente in conds2 ...
            if not True in map(lambda a: a.isOpposite(cond1),conds2):   #... E in conds2 non c'è nemmeno un suo opposto...
                output = addCondToExpr(output, cond1)                             #Aggiungi anche questa condizione
    return output
                
def actionUnion(domain, action1, action2):
    #Unisce le due azioni in una in modo tale che abbia le precondizioni della prima e gli effetti quelli totali
    #TEMP da fare se c'è una precondizione che sta nella seconda ma non negli effetti della prima
    name = action1.name+"-"+action2.name    #Il nome sarà il nome delle due azioni con il - in mezzo
    precondition = action1.precondition     #Le precondition sono quelle dell'azione 1
    currParameters = set(computeParametersInExpr(precondition))  #Sicuramente ci sono tutti i parametri della prima azione
    parma2toparam1 = computeDifferenceInParametersName(action1.effect,action2.precondition) #Dizionario che serve se i nomi dei parametri delle due azioni non corrispondono
    #Usa quel dizionario per cambiare i nomi dei parametri
    pre2paramsmore = set(changeParameters2Expr(action2.precondition, parma2toparam1))
    post2parammore = set(changeParameters2Expr(action2.effect, parma2toparam1))
    #Inserisco tutti i parametri e solo una volta
    parameters = currParameters | pre2paramsmore | post2parammore
    #Gli effetti sono l'unione degli effetti di 1 e 2
    effect = effectUnion(action1.effect,action2.effect)
    #Inserisco la nuova azione nel dominio
    newAction = Action(name, parameters, precondition, effect)
    domain.addAction(newAction)
    #Rimuovo l'azioni vecchie nel dominio
    domain.deleteAction(action1)
    domain.deleteAction(action2)

def checkPossibleActionUnion(domain, problem):      #Controlla se è possibile unire due azioni
#Puoi unire due azioni se la precondition di una equivale alla postcondition dell'altra
#e nessun altra azioni o il goal richiede qualcosa in queste precondizioni
    for action in domain.actions:
        effect = action.effect
        for other in domain.actions:
            if effect == other.precondition:        #Gli effetti di 'action' sono all'interno delle precondizioni di 'other'
                if action == other:     #in questo caso precondizioni e effetti di un azione coincidono... si può fare qualcosa
                    continue
                #print(f"Trovata! azione {action.name} con azione {other.name}")
                 
                #Controlla che queste non siano pre di qualcos'altro
                valid = True
                for cond in allCondinExp(other.precondition):  
                    if condInExp(cond,problem.goal): #Controlla che effetti non siano un goal
                        print(f"Condizione {cond} trovata nel goal")            #Temp
                        valid = False
                        break
                    for act in domain.actions:
                        if act == action or act == other:
                            continue
                        if condInExp(cond, act.precondition):
                            #print(f"trovata condizione {cond} in azione {act.name}")        #Temp
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    continue
                print(f"Posso unire queste due azioni: {action.name}, {other.name}")
                print("Starto l'unione")
                actionUnion(domain, action, other)
    print("Finito")

checkPossibleActionUnion(domain,problem)

print("Controllo se posso eliminare qualcosa")
def checkPossibleEliminateAction(domain, problem):
    #Puoi eliminare un azione se gli effetti non compaiono in nessuna
    #pre-condizione di altre azioni o nei goal
    for action in domain.actions:
        effectCond = allCondinExp(action.effect)
        forElimination = True
        for other in domain.actions:
            otherPreCond = allCondinExp(other.precondition)
            if any([x in effectCond for x in otherPreCond]):    #Se hanno almeno un elemento in comune passa alla prossima azione
                forElimination = False
                break
        #Ora se posso eliminarlo controllo che qualche effetto non sia nei goal
        if forElimination and not any(x in effectCond for x in allCondinExp(problem.goal)):
            #Adesso so che action è eliminabile
            print(f"Posso eliminare l'azione {action.name}")
            domain.deleteAction(action)
            print(f"Azione {action.name} eliminata")
            
checkPossibleEliminateAction(domain,problem)

def processTypeForWriting(types):
    #ritorna un array con tutti gli object (type) scritti correttamente per una stampa
    noneParent = []
    parent2child = {}
    elements_processed = []
    rows = []   #vettore di output, contine stringhe
    #Costruisci il dizionario parenti -> array di figli
    for ob in types:
        if not ob.parent:
            noneParent.append(ob.name)
            continue
        if ob.parent.name in parent2child.keys():
            parent2child[ob.parent.name].append(ob.name)
        else:
            parent2child[ob.parent.name] = [ob.name]
    #Ora inizia a scrivere, prima quelli che non hanno parenti
    for par in noneParent:
        try:
            elements = parent2child.pop(par)
            elements_processed += elements
            rows.append(" ".join(elements) + f" - {par}")
        except:
            print("C'è qualche problema, un NoneType!")          #Temp
    #Ora scrivi tutti, scrivendo prima quelli i cui parenti sono già stati scritti
    while len(parent2child)> 0:
        add_processed = []
        for elem in elements_processed:
            if elem in parent2child.keys():
                elements = parent2child.pop(elem)
                add_processed += elements
                rows.append(" ".join(map(str,elements)) + f" - {elem}")
        if len(add_processed) == 0:     #Se hai fatto un iterazione senza aggiungere nulla c'è qualche problema
            print("Problema, Non sono riuscito a mettere tutti") #Temp
            break
        elements_processed += add_processed
    return rows


# REWRITE TO FILE

fileNameDoOud = os.getcwd() + "\\Examples\\domain-processed.pddl"
def rewrite():
    with open(fileNameDoOud, "w") as f:
        #Write domain and domain name
        f.write(f"(define (domain {domain.name})\n")
        #write requirements
        if len(domain.requirements) > 0:
            f.write("\t(:requirements " + " ".join(map(str,domain.requirements)))
            f.write(")\n")
        #write typing
        if domain.typing:
            f.write("\t(:types \n\t\t")
            f.write("\n\t\t".join(processTypeForWriting(domain.objects)))
            f.write("\n\t)\n\n")
        #Write Predicates
        f.write(f"\t(:predicates\n\t\t")
        for i in range(len(domain.predicates)-1):
            f.write(f"({domain.predicates[i]})")
            f.write("\n\t\t")
        f.write(f"({domain.predicates[-1]})\n\t)\n\n")
        #Write actions
        for action in domain.actions:
            #Write aciton name
            f.write(f"\t(:action {action.name}\n")
            #write action parameter
            f.write("\t\t:parameters ("+ ' '.join(map(str,action.parameters)))
            f.write(")\n")
            #Write precondition
            f.write("\t\t:precondition ")
            f.write(str(action.precondition))
            f.write("\n")
            #Write effect
            f.write("\t\t:effect ")
            f.write(str(action.effect))
            f.write("\n\t)\n\n")
        f.write(")")
rewrite()