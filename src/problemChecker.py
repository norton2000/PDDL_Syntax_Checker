from .pddl import *
from .utility import *
from .tokenizer import *
from .domainChecker import checkName, expect, checkVariables, analyzeCond, extract

import re

def checkProblemDomain(lista, domain):
    expect(":domain",lista[0], domain)
    if len(lista) > 2:
        (word, n_line) = lista[2]
        raise SynError(f'The domain name must consist of only one word, find "{word}".', n_line, word)
    if lista[1][0] != domain.name:
        (word, n_line) = lista[1]
        raise SynError(f'The domain "{word}" is unknown. Maybe you meant "{domain.name}"', n_line, word)
    #Se si deve assegnare il dominio al problema qui, ora lo faccio all'inizio quando creo oggetto problem

def checkObjects(lista,domain,problem):
    expect(":objects",lista[0], domain)
    variables = checkVariables(lista[1:],domain,False) #False perché non sono variabili ma oggetti quindi non iniziano con ?
    #parameters = list(map(lambda elem: elem.name,variables))
    problem.setObjects(variables)

def checkTypingBetweenObject(parent, child):    #Dati tue type controlla se child è == a father oppure father è presente tra i parent dei parent di child
    if child == None:       #Caso base, non ho trovato il tipo "parent" tra i parent di child
        return False
    return child==parent or checkTypingBetweenObject(parent, child.parent)  #Passo ricorsivo

def checkSingleProblemCondition(cond,domain,problem):
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
            raise SynError(f'The object "{cond[i][0]}" Does not exist in the current problem.', n_line, cond[i][0])
        if(domain.typing):
            typeReal = obj.obj
            if not checkTypingBetweenObject(typeRequest,typeReal):
                nameReal = typeReal.name if typeReal else None
                requestName = typeRequest.name if typeRequest else None
                raise SynError(f'The object "{cond[i][0]}" is of the type "{nameReal}", whereas the predicate "{word}" wants as its {i} argument the type "{requestName}".', n_line, cond[i][0])
        objs.append(obj)
        i+=1
    #Uso il nome per creare un nuovo predicato perché quello che ho nel dominio non ha collegato gli oggetti giusti
    return Predicate(word,objs)
    
def checkInit(lista,domain,problem):
    expect(":init",lista[0], domain)
    for elem in lista[1:]:
        initCond = checkSingleProblemCondition(elem,domain,problem)
        problem.addCondition(initCond)
    
def checkGoal(lista,domain,problem):
    expect(":goal",lista[0], domain)
    parameters = list(map(lambda elem: elem.name,problem.objects))
    goal = analyzeCond(lista[1],parameters,"Goal",domain)
    problem.setGoal(goal)
   



def problemChecker(problemFileName, domain):
    problem = Problem(domain)
    try:
        input_filePr = open(problemFileName, "r").readlines()
        tokens = tokenize(input_filePr)
        next_token = next(tokens)
        if next_token[0] != "(":
            raise ParseError("Expected '(' at the beginning, got '%s'." % next_token[0])
        result = list(parse_list_aux(tokens))
        for tok in tokens:  # Check that generator is exhausted.
            raise ParseError("Unexpected token: %s." % tok)
        i=0
        expect("define",result[i], domain)  #define problem
        i += 1
        problem.name = checkName(result[i], domain,"problem")  #Problem name
        i += 1
        checkProblemDomain(result[i], domain)
        i += 1
        checkObjects(result[i],domain,problem)
        i += 1
        checkInit(result[i],domain,problem)
        i += 1
        checkGoal(result[i],domain,problem)
        return problem

    except ParseError as err:
        print(err)
    except (SynError,SupportException) as err:
        line = err.line
        word = err.word
        line_file = re.sub(r'^[\t\s]*|\t', '',input_filePr[line][:-1])
        print(f'  File "{problemFileName}", line {line+1}')
        print(f"    {line_file}")
        pos = findIndexInText(word,line_file)
        if pos != -1:
            print(" " * pos + "^")
        print(f'SyntaxPddlError: {err}')
    
    
