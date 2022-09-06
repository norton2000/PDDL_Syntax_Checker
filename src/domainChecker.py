from .pddl import *
from .utility import *
from .tokenizer import *

import re

SUPPORTED_REQUIREMENTS = ["typing", "strips", "adl", "negative-preconditions", "disjunctive-preconditions",
                          "existential-preconditions", "universal-preconditions", "quantified-preconditions",
                          "conditional-effects", "equality"]
                          
SUPPORTED_LOGIC = ["and", "or", "imply", "forall", "exists", "when", "not"]

KEY_WORD = [":action",":parameters", ":precondition", ":effect"]

current_line = None

def extract(token):
    global current_line 
    if type(token) == str:
        raise SynError(f"Missing an open round bracket before {token}", current_line, token)
    elif type(token) == int:
        raise SynError(f"Missing an open round bracket at the line {token}", token, "")
    elif type(token) == list:
        (word, n_line) = computeElemInList(token)
        current_line = n_line
        raise SynError(f'There is an closed round bracket missing before this parenthesis opening', n_line, "\("+word)
    elif type(token) == tuple:
        return token
    raise SynError("",0,"")      #Non può essere qualcosa diverso da tupla stringa o lista
        
#Function that take an expected expression and the expression and check that they are equal, if not they ryse an SynError.
def expect(expected, current_token, domain, err=True):
    if type(current_token) == list:
        return expect(expected, current_token[0], domain, err)
    (word, n_line) = extract(current_token)
    if not word == expected:
        if err:
            domain.addErrors(SynError(f'Expected "{expected}" but we have "{word}".', n_line, word))
        return False
    return True

def computeElemInList(elem):
    #Ritorna il primo elemento base (name, n_line) di una lista
    if type(elem) == list:
        return computeElemInList(elem[0])
    return elem
 
def expectStarting(expected, current_token, domain):
    (word, n_line) = extract(current_token)
    if not word[:len(expected)] == expected:
        domain.addErrors(SynError(f'Expected "{expected}" before "{word}".', n_line, word))
        return False
    return True

def checkName(lista, domain, subject="domain"):
    #subject è o domain o problem a seconda di quale nome si sta facendo il check
    if not expect(subject,lista[0], domain):
        return None
    if len(lista) > 2:
        (word, n_line) = extract(lista[2])
        domain.addErrors(SynError(f'The {subject} name can only have one word, find "{word}".', n_line, word))
    return lista[1][0]
    
def checkRequirements(lista, domain):
    expect(":requirements",lista[0], domain)
    for elem in lista[1:]:
        (req, n_line) = extract(elem)
        if not expectStarting(":",elem, domain):    #Se non inizia con due punti aggiungi l'errore e passa avanti
            continue
        if req[1:] not in SUPPORTED_REQUIREMENTS:
            domain.addErrors(SupportException(f"requirement {req[1:]} is not supported.",n_line,req))
            return
        if req[1:] == "typing" or req[1:] == "adl":
            domain.activeTyping();
        domain.addRequirement(req)

def addObjects(objsName, domain, parent=None):
    for objName in objsName:
        objExist = domain.getObject(objName)
        if objExist:
            objExist.parent = parent
        else:
            obj = Object(objName,parent)
            domain.addObject(obj)

def checkTypesObjects(lista, domain):
    expect(":types",lista[0], domain)
    waitingTypeFather = []
    i = 1
    while i<len(lista):
        (name,n_line) = extract(lista[i])
        if name == "-": #Allora l'elemento successivo sarà l'oggetto genitore di tutti quelli precedenti. 
            i+=1
            (name,n_line) = extract(lista[i])   
            parObj = domain.getObject(name)  
            if not parObj:  #Controllo che effettivamente esiste l'oggetto gentiore altrimenti lo creo
                parObj = Object(name)
                domain.addObject(parObj)
            addObjects(waitingTypeFather,domain, parObj)    #Tutta la lista di oggetti che era in attesa di genitore ora posso crearli
            waitingTypeFather = []
        else:       #Nuovo oggetto
            if name in waitingTypeFather or (domain.getObject(name) and domain.getObject(name).parent != None):     #Controllo se ho già un oggetto con questo nome
                #Se il parent è None vuol dire che vuoi definire adesso il suo parent quindi non è un errore
                domain.addErrors(SynError(f'type "{name}" already exist.', n_line, name))   #Altrimenti è un errore
                i+=1        #Dato che è un errore passa, salvati l'errore e passa al successivo
                continue
            waitingTypeFather.append(name)  #Inserisco nella lista degli oggetti da creare
        i+=1
    addObjects(waitingTypeFather, domain)   #Creo gli oggetti che non hanno genitori

'''  
def checkVariableList(lista):
    for elem in lista:
        expectStarting("?",elem)
'''
def checkPredicates(lista, domain):
    expect(":predicates",lista[0], domain)
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
        (elem,n_line) = extract(lista[i])
        if elem in KEY_WORD:    #Se è una parola chiave allora hai scordato di chiudere la parentesi ha quello prima
            (elem,n_line) = lista[i-1]
            raise SynError(f'A closed parenthesis is missing after  "{elem}"', n_line, elem)
        if elem == "-": #Allora l'elemento successivo sarà l'oggetto di tutti i parametri precedenti. 
            i+=1
            (elem,n_line) = extract(lista[i])   
            typ = domain.getObject(elem) 
            if not typ:  #Controllo che effettivamente esiste l'oggetto gentiore
                domain.addErrors(SynError(f'types "{elem}" doesn\'t exist.', n_line, elem)) #Se non esiste mi salvo l'errore
                i+=1            #E passo diretto al successivo
                continue 
            addVariables(variables,waitingType,typ)    #Inserisce le variabili in waitingType di tipo typ all'interno della lista variables
            waitingType = []
        else:
            if variable:
                expectStarting("?",lista[i], domain)
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
    if not predicate:   #Se non l'ho trovato come predicato allora c'è qualche errore
        if name != "=":     # anche se posso accettare tranquillamente = come predicato
            domain.addErrors(SynError(f'The predicate "{name}" does not exist in action {nameAction}.', n_line, name))  #Salvati l'errore
            return  #E finisci di controllare questo predicato, passa al prossimo predicato
        predicate = Predicate("=",['a','b'])
    if not predicate.lenArguments()==len(params):   #Se vedi che hai più argomenti di quanto 
        domain.addErrors(SynError(f'Predicate "{name}" must have {predicate.lenArguments()} arguments in action {nameAction}. Missing a closing parenthesis closing the predicate', n_line, name))
        return  #E finisci di controllare questo predicato, passa al prossimo predicato
    for param in params:
        if param[0] not in parameters:
            domain.addErrors(SynError(f'Parameters "{param[0]}" does not exist in action {nameAction}.', param[1], param[0]))
            return  #E finisci di controllare questo predicato, passa al prossimo predicato

def computeLogicExpression(lista,parameters,nameAction,domain,notAllowed = [],currNotAllowed = []):
    if type(lista[0]) == str:   #Se è str vuol dire che non è stata messa la parentesi tonda prima dell'espressione logica
        if lista[0] in KEY_WORD:    #Se questa è una parola chiave allora manca una parentesi che chiude prima
            raise SynError(f'A closed parenthesis is missing before  "{lista[0]}"', lista[1], lista[0])   #Lancia un errore bloccante
        domain.addErrors(SynError(f'Need a parentesis before {lista[0]} in action {nameAction}',lista[1], lista[0]))
        return False #Allora aggiungi l'errore e passa avanti (prossima exp logica) [Aggiungo False e non None per andare ancora avanti]
    if type(lista[0]) == list:  #Se è una lista vuol dire che ci sono troppe parentesi
       (name,n_line) = computeElemInList(lista[0])
       domain.addErrors(SynError(f'Too many parentheses enclosing {name} in action {nameAction}',n_line, name))
       return None #Allora aggiungi l'errore e passa avanti (prossima exp logica)
    (exp,n_line) = extract(lista[0])
    
    if exp in notAllowed or exp in currNotAllowed:  #Se stai usando un espressione non permessa (esempio: and dopo un and)
        domain.addErrors(SynError(f'You cannot use the expression "{exp}" here', n_line, exp))
        return None     #Aggiungi l'errore e passa avanti (prossima exp logica)
    
    if exp == "and" or exp == "or":
        arguments = computeListLogicExpression(lista[1:],parameters,nameAction,domain,notAllowed,currNotAllowed=[exp]) #Dopo un and non ci può essere un altro and (Stessa cosa con or)
        return LogicExpression(exp, arguments)
    elif exp == "imply" or exp == "when":   #Imply work in progress
        arguments1 = analyzeCond(lista[1],parameters,nameAction,domain,notAllowed)
        arguments2 = analyzeCond(lista[2],parameters,nameAction,domain,notAllowed)
        return LogicExpression(exp, (arguments1,arguments2))
    elif exp == "forall" or exp == "exists":
        variables = checkVariables(lista[1], domain)
        newparameters = list(map(lambda elem: elem.name,variables))
        if set(newparameters).intersection(parameters):         #Controlla se stai usando dei parametri già usati
            commonParameter = set(newparameters).intersection(parameters).pop()
            domain.addErrors(SynError(f"You shouldn't use the same variable in a forall or exists clause as you have in the parameters. Check {commonParameter}", n_line, commonParameter))
            return None      #Aggiungi errore, ritorna None e passa avanti
        if lista[2][0][0] == "when":
            arguments = computeListLogicExpression(lista[2][1:],parameters+newparameters,nameAction,domain,notAllowed)
            return LogicExpression(exp, (variables,[LogicExpression("when",arguments)]))
        arguments = computeListLogicExpression(lista[2:],parameters+newparameters,nameAction,domain,notAllowed)
        return LogicExpression(exp, (variables,arguments))
    elif exp == "not" and lista[1][0][0] == "exists":           #Per il (not (exists ...))
        arguments = computeListLogicExpression(lista[1:],parameters,nameAction,domain,notAllowed)
        return LogicExpression(exp, arguments)
        
    else:
        return analyzeSingleCond(lista,parameters,nameAction, domain)

def computeListLogicExpression(lista,parameters,nameAction,domain,notAllowed = [],currNotAllowed = []):
    result = []
    for elem in lista:
        nextExp = computeLogicExpression(elem,parameters,nameAction,domain,notAllowed,currNotAllowed)
        if nextExp:         #Se è None vuol dire che c'è stato un errore. Non serve inserire None nella lista
            result.append(nextExp)
        elif nextExp==False: break         #Altrimenti esci dall'iterazione e passa alla prossima espressione logica
    return result
    
def analyzeSingleCond(elem, parameters, nameAction, domain):
    if elem[0][0] in KEY_WORD:    #Se è una parola chiave allora hai scordato di chiudere la parentesi ha quello prima
        (elem,n_line) = elem[0]
        raise SynError(f'A closed parenthesis is missing before  "{elem}"', n_line, elem)
    positive = elem[0][0] != "not"      #False if the sentence is a negation
    if not positive:
        if type(elem[1]) != list:      #Se dopo Not non metti una parentesi tonda...
            domain.addErrors(SynError(f' Error in action {nameAction}. After "not" comes a round bracket.', elem[0][1], "not"))
            return None     #Aggiungi l'errore, ritorna None e passa avanti
        if len(elem)> 2:
            raise SynError(f' Error in action {nameAction}. You can use "not" with only one condition. Close the not parenthesis after the condition', elem[0][1], "not")
        elem = elem[1]
    name = elem[0][0]
    analyzePredInCond(name, elem[1:], elem[0][1], parameters, nameAction, domain)
    arguments = list(map(lambda e: e[0],elem[1:]))
    return Condition(name, arguments, positive)

def analyzeCond(lista, parameters,nameAction,domain,notAllowed = []):
    return computeLogicExpression(lista,parameters,nameAction,domain,notAllowed)
        
def checkAction(action,domain):
    expect(":action",action[0],domain)
    name = action[1][0]
    expect(":parameters",action[2], domain)
    variables = checkVariables(action[3], domain)
    #checkVariableList(action[3])
    parameters = list(map(lambda elem: elem.name,variables))
    expect(":precondition",action[4], domain)
    prec = analyzeCond(action[5],parameters,name,domain)
    expect(":effect",action[6], domain)
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
        result = list(parse_list_aux(tokens, domain))
        for tok in tokens:  # Check that generator is exhausted.
            raise ParseError("Unexpected token: %s." % tok)
        i=0
        expect("define",result[i], domain)  #define domain
        i += 1
        domain.name = checkName(result[i], domain,"domain")  #Domain name
        i += 1
        if(expect(":requirements",result[i], domain,False)):
            checkRequirements(result[i], domain)
            i += 1
        if domain.typing and expect(":types",result[i], domain,False):
            checkTypesObjects(result[i], domain)
            i += 1
        if(expect(":constants",result[i], domain,False)):
            raise SupportException("constants are not supported.",result[i][0][1],result[i][0][0])
        checkPredicates(result[i], domain)  #Check Predicates
        i += 1
        while i<len(result):
            checkAction(result[i],domain)
            i += 1
         
        if domain.errors:
            if len(domain.errors)>1:
                print(f"\n FOUND {len(domain.errors)} ERRORS IN THE DOMAIN:\n")
            for err in domain.errors:
                printSynError(err, domainFileName, input_file)
                print()
            return None
        return domain

    except ParseError as err:
        print(f'Error parsing file "{domainFileName}"')
        print(err)
    
    except (SynError,SupportException) as error:
        if domain and domain.errors:
            print(f"\n FOUND {len(domain.errors)+1} ERRORS IN THE DOMAIN:\n")
            for err in domain.errors:
                printSynError(err, domainFileName, input_file)
                print()
        printSynError(error, domainFileName, input_file)
        print()
        '''
        line = err.line
        word = err.word
        line_file = re.sub(r'^[\t\s]*|\t', '',input_file[line][:-1])
        print(f'  File "{domainFileName}", line {line+1}')
        print(f"    {line_file}")
        pos = findIndexInText(word,line_file)
        if pos != -1:
            print(" " * pos + "^")
        print(f'SyntaxPddlError: {err}')
        '''
