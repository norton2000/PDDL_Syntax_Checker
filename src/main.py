from .pddl import *
from .problemChecker import problemChecker
from .domainChecker import domainChecker
from .optimizer import checkPossibleActionUnion, checkPossibleEliminateAction, actionUnion, rewrite

import os

def request(text):
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
            

def start(domainFileName, problemFileName):

    domain = domainChecker(domainFileName)
    print("-------------------------DOMAIN-------------------------")
    print(domain)
    if problemFileName:
        problem = problemChecker(problemFileName, domain)
        print("\n-------------------------PROBLEM-------------------------")
        print(problem)
    else:
        problem = None
    
    if problem:
        print("\n-------------------------START OPTIMIZATION-------------------------")
        changed = False
        print("Check some action to union")
        actions2merge = checkPossibleActionUnion(domain,problem)
        if actions2merge:
            for (a1,a2) in actions2merge:
                r = request(f"Find {a1.name} and {a2.name}, do you want to merge them? [y] [n] ")
                if r:
                    actionUnion(domain, a1, a2)
                    changed = True
                    print(f"{a1.name} and {a2.name} merged into {a1.name}-{a2.name}")
        
        print("Check some action to be eliminated")
        actions2delete = checkPossibleEliminateAction(domain,problem)
        if actions2delete:
            for a in actions2delete:
                r = request(f"Find {a.name}, do you want to delete it? [y] [n] ")
                if r:
                    domain.deleteAction(a)
                    changed = True
                    print(f"action {a.name} deleted")
        
        if changed:
            fileNameDoOud = os.getcwd() + "\\Examples\\domain-processed.pddl"
            rewrite(domain,fileNameDoOud)
            print(f"The new modified domain is {fileNameDoOud}")
        else:
            print("Nothing else to optimize")
    
    
