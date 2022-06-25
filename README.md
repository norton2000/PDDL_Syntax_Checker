# Pddl_Syntax_Checker
 
Pddl_Syntax_Checker is a command-line python software that correct the syntax of PDDL domains and problems and which allows basic optimizations such as merging two actions or eliminating unusable actions.


## Usage

To use open the command prompt in the root directory and execute:
```java
python .\syntaxChecker.py -d PATH_DOMAIN_FILE.pddl -p PATH_PROBLEM_FILE.pddl
```
We pass as parameter -d the domain file and as parameter -p (optionae) the problem file. 

You can enter the full PATH of the file or the relative PATH with respect to the EXEMPLES folder.


## Example

In the Examples folder there are several domains and problems, in particular in subfolders there are all the domains of The First International Planning Competition of 1998. In addition to this there are example domains with errors or with the possibility of using the optimizer.

you can see a demonstration video by clicking [here](https://youtu.be/4QuSJSSz8I4)


## PDDL Compatibility

This syntax checker is compatible with all the main features of PDDL 1.2. For full details on compatibility read the report.pdf
