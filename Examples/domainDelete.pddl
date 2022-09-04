; Domain gripper-strips modified by adding a new action "turn-off" and a new predicate "turned-off ?g - gripper".
; If you associate with problem pddl "problem.pddl" then this action turns out to be unnecessary because it is redundant
; (the goal does not require the gripper to be turned-off).
; You want to show that the optimizer recognizes that this action is unnecessary and will remove it
; The command to perform this optimization is: 
; python ./syntaxChecker.py -d Examples/domainDelete.pddl -p Examples/problem.pddl -o


(define (domain gripper-strips)
   (:requirements :strips :typing)
   (:types ball gripper room)
   (:predicates
        (at-robby ?r - room)
        (at ?b - ball ?r - room)
        (free ?g - gripper)
        (carry ?o - ball ?g - gripper)
		(turned-off ?g - gripper))


   (:action move
       :parameters  (?from ?to - room)
       :precondition (and (at-robby ?from))
       :effect (and  (at-robby ?to)
             (not (at-robby ?from))))	

	
   (:action pick
       :parameters (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (at ?obj ?room) (at-robby ?room) (free ?gripper))
       :effect (and (carry ?obj ?gripper)
		    (not (at ?obj ?room)) 
		    (not (free ?gripper))))


   (:action drop
       :parameters  (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (carry ?obj ?gripper) (at-robby ?room))
       :effect (and (at ?obj ?room)
		    (free ?gripper)
		    (not (carry ?obj ?gripper))))


	(:action turn-off
		:parameters (?gripper - gripper)
		:precondition (free ?gripper)
		:effect (turned-off ?gripper)))