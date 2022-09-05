# Pddl_Syntax_Checker
 
Pddl_Syntax_Checker is a command-line python software that correct the syntax of PDDL domains and problems and which allows basic optimizations such as merging two actions or eliminating unusable actions.
In addition to the syntax checker and optimizer, it is possible (on UNIX only) to use the [Fast downward](https://www.fast-downward.org/) planner to search for a plan.


## Usage

To use Pddl_Syntax_Checker open the command prompt in the root directory and execute:
```java
python .\syntaxChecker.py -d PATH_DOMAIN_FILE.pddl -p PATH_PROBLEM_FILE.pddl
```
We pass as parameter -d the domain file and as parameter -p (optional) the problem file.

You can enter the full PATH of the file or the relative PATH with respect to the current folder.

Using the -o parameter will activate optimization, so the program will either try to merge two actions that are bound to occur in succession or eliminate actions that are redundant for the current problem. An output file in case optimization occurs will be generated in the "out" folder.

Using the -e parameter it will be possible to search for a plan using the Fast Downward planner. To initialize the planner read the section [Planner](#planner-fast-downward).
Additional parameters to be passed to Fast Downward can be entered as a string after the -e parameter. If no parameter is entered, the standard parameters "--search astar(lmcut())" will be used. For the parameters of Fast Downward read the [official website](https://www.fast-downward.org/PlannerUsage)

The complete command with optimization and planning is:
```java
python .\syntaxChecker.py -d PATH_DOMAIN_FILE.pddl -p PATH_PROBLEM_FILE.pddl -o -e "FAST_DOWNWARD_PARAMETERS"
```

## Planner (Fast Downward)
Inside the downward folder is the Fast Downward software (realase 22.06). In order to use the planner, you must first enter the downward folder and run the command .\build.py
```bash
cd downward
./build.py
```
For any problems with the build, visit the [FastDownward site](https://www.fast-downward.org/) and read about compatibility.
The software has been tested and works correctly on:
- UBUNTU 16.4 LTS
- UBUNTU 20.04

## Example

In the Examples folder there are several domains and problems, in particular in subfolders there are all the domains of The First International Planning Competition of 1998. In addition to this there are example domains with errors or with the possibility of using the optimizer, In particular we have:
- **domain.pddl**: contains the error-free "gripper" domain. It is the domain from which all the modified domains described below originate.
- **problem.pddl**: Simple and correct problem associated with the domain "gripper"
- **domainWithError.pddl**: The same "gripper" domain but with several errors. It is useful to show how Syntax Checker works when it finds errors.
- **problemWithError.pddl**: The same problem related to "gripper" but with different errors. It is useful to show how Syntax Checker works when it finds errors.
- **domainDelete.pddl**: The same "gripper" domain but with the addition of a new action that turns off the gripper. If you want to generate a plan with this domain and the problem contained in problem.pddl this new action turns out to be useless. If you use the Syntax Checker with the optimizer (parameter -o) the unnecessary action will be recognized and removed. For this test use the following code:
```bash
python .\syntaxChecker.py -d Examples\domainDelete.pddl -p Examples\problem.pddl -o
```
- **domainMerge.pddl**: The same "gripper" domain but the pick action has been broken down into two actions, one that prepares the gripper for gripping the object and one that actually takes the object. If you want to generate a plan with this domain and the problem contained in problem.pddl, these two actions will always be used consecutively. If you use the Syntax Checker with the optimizer (parameter -o) these two actions that are always achieved will be recognized and merged. For this test use the following code:
```bash
python .\syntaxChecker.py -d Examples\domainMerge.pddl -p Examples\problem.pddl -o
```

## PDDL Compatibility

This syntax checker is compatible with all the main features of PDDL 1.2. For full details on compatibility read the report.pdf
