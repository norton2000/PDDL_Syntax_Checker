from .pddl import *
from .problemChecker import problemChecker
from .domainChecker import domainChecker
from .optimizer import checkPossibleActionUnion, checkPossibleEliminateAction, actionUnion, rewrite

import os

def checkPathFile(domainFileName, problemFileName):
    #Costruisce il path assoluto se il path ricevuto in input è relativo alla cartella Exemples
    if domainFileName[1] != ":" :   #Se non è un path assoluto
        domainFileName = os.path.join(os.getcwd(),"Examples",domainFileName)
    if problemFileName and problemFileName[1] != ":":
        problemFileName = os.path.join(os.getcwd(),"Examples",problemFileName)
    
    if not os.path.exists(domainFileName):
        raise FileNotFoundError(domainFileName)
    if problemFileName and not os.path.exists(problemFileName):
        raise FileNotFoundError(problemFileName)
    
    return domainFileName, problemFileName

def requestYN(text):
    #Richiede in input Yes o No (con testo passato come parametro) e ne ritorna un booleano come output
    i = 0
    while i < 5:
        ans = input(text)
        if any(ans.lower() == f for f in ["yes", 'y', '1', 'ye']):
            return True
        elif any(ans.lower() == f for f in ['no', 'n', '0']):
            return False
        else:
            i+=1
            print('Please enter yes or no')
    print("too many attempts, I have not made the change")
            
def requestDoPrOp(text):
    #Accetta come input (con testo personalizzato) d o domain (0) p o problem (1) o 'o' o optimize (2) e ritorna i numeri corrispondenti
    i = 0
    while i < 5:
        ans = input(text)
        if any(ans.lower() == f for f in ["d", 'domain', 'dom']):
            return 0
        elif any(ans.lower() == f for f in ['p', 'pro', 'prob', 'problem']):
            return 1
        elif any(ans.lower() == f for f in ['o', 'opti', 'optimize', 'optimizer']):
            return 2
        elif any(ans.lower() == f for f in ['q', 'quit', 'exit', '0']):
            return 9
        else:
            i+=1
            print('Please enter a option or write \'q\' or \'quit\' to exit')
    print("too many attempts, quit program...")
    return 9

def start(domainFileName, problemFileName):
    try:
        domainFileName, problemFileName = checkPathFile(domainFileName, problemFileName)
    except FileNotFoundError as e:
        print("\nFile not found! Check the path of the file:")
        print(str(e)+"\n")
        return
    
    domain = domainChecker(domainFileName)
    #print("-------------------------DOMAIN-------------------------")
    #print(domain)
    if problemFileName and domain:
        problem = problemChecker(problemFileName, domain)
        #print("\n-------------------------PROBLEM-------------------------")
        #print(problem)
    else:
        problem = None
    if domain and not problemFileName:
        print("The syntax of the domain is correct!")
        num = 5
        print("Enter an option from those listed")
        num = requestDoPrOp("[d] [domain] visualize domain. [q] exit: ")
        if num == 0:
            print()
            print(domain)
            print()
        elif num == 1 or num == 2:
            print("Pass the problem path as a parameter for this function")
        elif num == 9:
            print("Goodbye!")
        
    elif domain and problem:
        print("The syntax of the domain and problem are correct!")
        num = 5
        while num != 9:
            print("\nEnter an option from those listed")
            num = requestDoPrOp("[d] visualize domain. [p] visualize problem. [o] check optimization. [q] exit: ")
            if num == 0:    #Print dominio
                print()
                print(domain)
                print()
            elif num == 1:  #Print problem
                print()
                print(problem)
                print()
            elif num == 9:  #Exit
                print("Goodbye!")
            elif num == 2:  #Check Optimization
                changed = False
                actions2merge = checkPossibleActionUnion(domain,problem)
                if actions2merge:
                    for (a1,a2) in actions2merge:
                        r = requestYN(f"Find {a1.name} and {a2.name} that can be combined, do you want to merge them? [y] [n] ")
                        if r:
                            actionUnion(domain, a1, a2)
                            changed = True
                            print(f"{a1.name} and {a2.name} merged into {a1.name}-{a2.name}")
                
                actions2delete = checkPossibleEliminateAction(domain,problem)
                if actions2delete:
                    for a in actions2delete:
                        r = requestYN(f"Find {a.name} that can be removed, do you want to delete it? [y] [n] ")
                        if r:
                            domain.deleteAction(a)
                            changed = True
                            print(f"action {a.name} deleted")
                
                if changed:
                    fileNameDoOud = os.getcwd() + "\\out\\domain-processed.pddl"
                    rewrite(domain,fileNameDoOud)
                    print(f"The new modified domain is {fileNameDoOud}")
                else:
                    print("Nothing to optimize")
    
    
