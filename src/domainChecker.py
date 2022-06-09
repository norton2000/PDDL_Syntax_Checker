from .pddl import *
from .utility import *
from .tokenizer import *

SUPPORTED_REQUIREMENTS = ["typing", "strips", "adl", "negative-preconditions"]

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
    
def checkRequirements(lista, domain):
    expect(":requirements",lista[0])
    for (req,n_line) in lista[1:]:
        expectStarting(":",(req,n_line))
        if req[1:] not in SUPPORTED_REQUIREMENTS:
            raise SupportException(f"requirement {req[1:]} is not supported.",n_line,req)
            return
        if req[1:] == "typing" or req[1:] == "adl":
            domain.activeTyping();
        domain.addRequirement(req)

def addObjects(objsName, domain, parent=None):
    for objName in objsName:
        obj = Object(objName,parent)
        domain.addObject(obj)

def checkTypesObjects(lista, domain):
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
            addObjects(waitingTypeFather,domain, parObj)    #Tutta la lista di oggetti che era in attesa di genitore ora posso crearli
            waitingTypeFather = []
        else:       #Nuovo oggetto
            if name in waitingTypeFather or domain.getObject(name):     #Controllo se ho già un oggetto con questo nome
                raise SynError(f'type "{name}" already exist.', n_line, name)
            waitingTypeFather.append(name)  #Inserisco nella lista degli oggetti da creare
        i+=1
    addObjects(waitingTypeFather, domain)   #Creo gli oggetti che non hanno genitori
        
def checkVariableList(lista):
    for elem in lista:
        expectStarting("?",elem)

def checkPredicates(lista, domain):
    expect(":predicates",lista[0])
    for predicate in lista[1:]:
        checkSinglePredicate(predicate, domain)

def addVariables(variables, newVariablesName, typ=None):
    for name in newVariablesName:
        variables.append(Parameter(name,typ))

def checkVariables(lista, domain, variable=True):
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
    
def checkSinglePredicate(pred, domain):
    name = pred[0][0]
    variables = checkVariables(pred[1:], domain)
    predicate = Predicate(name,variables)
    domain.addPredicate(predicate)

def analyzePredInCond(name, params, n_line, parameters, nameAction, domain):
    predicate = domain.findPredicate(name)
    if not predicate:
        raise SynError(f'The predicate "{name}" does not exist in action {nameAction}.', n_line, name)
    if not predicate.lenArguments()==len(params):
        raise SynError(f'Predicate "{name}" must have {predicate.lenArguments()} arguments, find {len(params)} arguments in action {nameAction}.', n_line, name)
    for param in params:
        if param[0] not in parameters:
            raise SynError(f'Parameters "{param[0]}" does not exist in action {nameAction}.', param[1], param[0])

def computeLogicExpression(lista,parameters,nameAction,domain,notAllowed = [],currNotAllowed = []):
    (exp,n_line) = lista[0]
    
    if exp in notAllowed or exp in currNotAllowed:
        raise SynError(f'You cannot use the expression "{exp}" here', n_line, exp)
    
    if exp == "and" or exp == "or":
        arguments = computeListLogicExpression(lista[1:],parameters,nameAction,domain,notAllowed,currNotAllowed=[exp]) #Dopo un and non ci può essere un altro and (Stessa cosa con or)
        return LogicExpression(exp, arguments)
    elif exp == "imply":   #Imply work in progress
        arguments1 = analyzeCond(lista[1],parameters,nameAction,domain,notAllowed)
        arguments2 = analyzeCond(lista[2],parameters,nameAction,domain,notAllowed)
        return LogicExpression(exp, (arguments1,arguments2))
    elif exp == "forall" or exp == "exists":
        variables = checkVariables(lista[1], domain)
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
        return analyzeSingleCond(lista,parameters,nameAction, domain)

def computeListLogicExpression(lista,parameters,nameAction,domain,notAllowed = [],currNotAllowed = []):
    result = []
    for elem in lista:
        result.append(computeLogicExpression(elem,parameters,nameAction,domain,notAllowed,currNotAllowed))
    return result
    
def analyzeSingleCond(elem,parameters,nameAction, domain):
    positive = elem[0][0] != "not"      #False if the sentence is a negation
    if not positive:
        elem = elem[1]
    name = elem[0][0]
    analyzePredInCond(name, elem[1:], elem[0][1], parameters,nameAction, domain)
    arguments = list(map(lambda e: e[0],elem[1:]))
    return Condition(name, arguments, positive)

def analyzeCond(lista, parameters,nameAction,domain,notAllowed = []):
    return computeLogicExpression(lista,parameters,nameAction,domain,notAllowed)
        
def checkAction(action,domain):
    expect(":action",action[0],domain)
    name = action[1][0]
    expect(":parameters",action[2])
    variables = checkVariables(action[3], domain)
    #checkVariableList(action[3])
    parameters = list(map(lambda elem: elem.name,variables))
    expect(":precondition",action[4])
    prec = analyzeCond(action[5],parameters,name,domain)
    expect(":effect",action[6])
    eff = analyzeCond(action[7],parameters,name,domain,notAllowed=["or"])
    action = Action(name, variables, prec, eff)
    domain.addAction(action)



def domainChecker(domainFileName):
    domain = Domain()
    try:
        input_file = open(domainFileName, "r").readlines()
        tokens = tokenize(input_file)
        next_token = next(tokens)
        if next_token[0] != "(":
            raise ParseError("Expected '(' at the beginning, got '%s'." % next_token[0])
        result = list(parse_list_aux(tokens))
        for tok in tokens:  # Check that generator is exhausted.
            raise ParseError("Unexpected token: %s." % tok)
        i=0
        expect("define",result[i])  #define domain
        i += 1
        domain.name = checkName(result[i],"domain")  #Domain name
        i += 1
        if(expect(":requirements",result[i],False)):
            checkRequirements(result[i], domain)
            i += 1
        if domain.typing and expect(":types",result[i],False):
            checkTypesObjects(result[i], domain)
            i += 1
        checkPredicates(result[i], domain)  #Check Predicates
        i += 1
        while i<len(result):
            checkAction(result[i],domain)
            i += 1

    except ParseError as err:
        print(err)
    except (SynError,SupportException) as err:
        line = err.line
        word = err.word
        print(f'  File "{domainFileName}", line {line+1}')
        print(f"    {input_file[line][:-1]}")
        pos = input_file[line].find(word)
        if pos != -1:
            print(" " * (pos+4) + "^")
        print(f'SyntaxPddlError: {err}')
    
    return domain
    