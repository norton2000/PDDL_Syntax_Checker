from .pddl import *

## OPTIMIZING AUXILIARY FUNCTIONS

def addCondToExpr(expr, cond):
    #Funzione che aggiunge una condizione a qualsiasi espressione
    if isinstance(expr, LogicExpression):
        expr.addCondToArgument(cond)
        return expr
    if isinstance(expr, Condition): #Se l'espressione è una condizione allora la fa diventare un espressione logica con and e con entrambe le condizioni
        return LogicExpression("and", [expr, cond])
    return NotImplemented   #Se non è ne una Condition ne una LogicExpression c'è qualcosa che non va, non è stato implementato per questo

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
                print(f"Error in merging actions: The parameters of condition {cond} do not correspond")
            if params != params2:       #Se i paramtri dei due sono diversi allora bisogna inserirli nel dizionario
                for i, param in enumerate(params):
                    if params2[i]!=param and not params2[i] in paramname2namefinal.keys():  #Se è diverso e non è già nel dizionario
                        paramname2namefinal[params2[i]] = param     #Inserisci nel dizionario la coppia param2-param
        else:
            print("Error in merging actions")
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
    actions2merge = []      #list of action tuples to join
    for action in domain.actions:
        effect = action.effect
        for other in domain.actions:
            if effect == other.precondition:        #Gli effetti di 'action' sono all'interno delle precondizioni di 'other'
                if action == other:     #in questo caso precondizioni e effetti di un azione coincidono... si può fare qualcosa
                    continue
                #Controlla che queste non siano pre di qualcos'altro
                valid = True
                for cond in allCondinExp(other.precondition):  
                    if condInExp(cond,problem.goal): #Controlla che effetti non siano un goal
                        valid = False
                        break
                    for act in domain.actions:
                        if act == action or act == other:
                            continue
                        if condInExp(cond, act.precondition):
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    continue
                #print(f"Posso unire queste due azioni: {action.name}, {other.name}")
                #print("Starto l'unione")
                #actionUnion(domain, action, other)
                actions2merge.append((action,other))
    return actions2merge
#checkPossibleActionUnion(domain,problem)

def OnlyCondInDomain(domain):
    #Funzione che prende come input un dominio e ritorna una lista contenente tuple
    #(nomeAzione,CondInPre,CondInEff)
    result = []
    for action in domain.actions:
        condInPre = allCondinExp(action.precondition)
        condInEff = allCondinExp(action.effect)
        result.append((action.name, condInPre, condInEff))
    return result

def allNameInList(lis):
    return [x.name for x in lis]

def checkPossibleEliminateAction(domain, problem):
    #Puoi eliminare un azione se gli effetti non compaiono in nessuna
    #pre-condizione di altre azioni o nei goal (1), OPPURE se almeno una precondizione
    #non è presente in nessun effetto di altre azioni oppure nell'init
    actions2Eliminate = []        # Output, contains the actions that can be deleted
    actionsCond = OnlyCondInDomain(domain)
    
    for (actionName,condInPre,condInEff) in actionsCond:
        variable = [False] * len(condInPre)
        forElimination1, forElimination2 = True, True
        for (otherName,otherCondInPre,otherCondInEff) in actionsCond:
            if otherName == actionName: #Non analizzare con la stessa azione
                continue
            #Controlla se gli effetti azioneranno qualche altra precondizione
            if forElimination1 and any([x in condInEff for x in otherCondInPre]):    #Se hanno almeno un elemento in comune passa alla prossima azione
                forElimination1 = False
            #Controlla se le precondizioni possono essere azionate da qualche effetto
            if forElimination2:
                #Controlla finché non vedi che tutte le precondizioni copaiono negli effetti di qualcosa
                curr = [x in otherCondInEff for x in condInPre]
                variable = [x or y for (x, y) in zip(variable, curr)]    
                if all(variable):
                    forElimination2 = False
        
        #Ora se posso eliminarlo controllo:
        #  -Che qualche effetto non sia nei goal (per 1)
        #  -Che qualche precondizione non sia nell'init (per 2)
        if forElimination1 and not any(x in condInEff for x in allCondinExp(problem.goal)):
            #Adesso so che action è eliminabile
            action = domain.findAction(actionName)
            actions2Eliminate.append(action)
            continue
        if forElimination2:
            initNames = allNameInList(problem.init)
            for i in range(len(variable)):
                if not variable[i]:     #Se questa condizione non è presente in nessun effetto, cerca tra init
                    if condInPre[i].positive and not (condInPre[i].name in initNames): 
                    #... Si può eliminare solo se è positiva e non è nell'init
                        #Adesso so che action è eliminabile
                        action = domain.findAction(actionName)
                        actions2Eliminate.append(action)
                        break
    return actions2Eliminate
    
    

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
        if par in parent2child:     #Se ha dei figli allora scrivi figlio - padre
            elements = parent2child.pop(par)
            elements_processed += elements
            rows.append(" ".join(elements) + f" - {par}")
        else:                       #Se non ha figli allora scrivilo senza -
            rows.append(par)
    #Ora scrivi tutti, scrivendo prima quelli i cui parenti sono già stati scritti
    while len(parent2child)> 0:
        add_processed = []
        for elem in elements_processed:
            if elem in parent2child.keys():
                elements = parent2child.pop(elem)
                add_processed += elements
                rows.append(" ".join(map(str,elements)) + f" - {elem}")
        if len(add_processed) == 0:     #Se hai fatto un iterazione senza aggiungere nulla c'è qualche problema
            break
        elements_processed += add_processed
    return rows


# REWRITE TO FILE
def rewrite(domain,fileNameDoOud):
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