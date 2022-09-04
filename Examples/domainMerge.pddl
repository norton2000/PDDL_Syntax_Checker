; The gripper domain was modified by decomposing the "pick" action into two actions "prepare_grab" and "grab."
; It is intended to show that by using the file "problem.pddl" as the problem, since the two added actions must necessarily be executed in sequence,
; it does not make sense to execute prepare_grab without performing grab, then the optimizer will recognize this and merge them into a single action.
; The command to perform this optimization is: 
; python ./syntaxChecker.py -d Examples/domainMerge.pddl -p Examples/problem.pddl -o


(define (domain gripper-strips)
   (:requirements :strips :typing)
   (:types ball gripper room)
   (:predicates
        (at-robby ?r - room)
        (at ?b - ball ?r - room)
        (free ?g - gripper)
        (carry ?o - ball ?g - gripper)
		(object-in-position-to-grab ?g - gripper ?o - ball ?r - room))


   (:action move
       :parameters  (?from ?to - room)
       :precondition (and (at-robby ?from))
       :effect (and  (at-robby ?to)
             (not (at-robby ?from))))
	
	
   (:action prepare_grab
       :parameters (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (at ?obj ?room) (at-robby ?room) (free ?gripper))
       :effect (object-in-position-to-grab ?gripper ?obj ?room))

	(:action grab
       :parameters (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (object-in-position-to-grab ?gripper ?obj ?room)
       :effect (and (not (object-in-position-to-grab ?gripper ?obj ?room))
			(carry ?obj ?gripper)
		    (not (at ?obj ?room)) 
		    (not (free ?gripper))))


   (:action drop
       :parameters  (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (carry ?obj ?gripper) (at-robby ?room))
       :effect (and (at ?obj ?room)
		    (free ?gripper)
		    (not (carry ?obj ?gripper)))))
			