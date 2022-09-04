; Pddl domain file containing some typical errors to show how the program behaves in front of them.
; The errors in particular are:
; 1) line 15, "?b" was put "cube" type that does not exist instead of "ball"
; 2) line 16, Missing question mark before "g" which are needed for variables
; 3) line 21, It says ":parameter" instead of ":parameters", one "s" is missing
; 4) line 22, "at-robby ?from" has to be inside brackets 
; 5) line 29, "?gri" is not a parameter that exists, "?gripper" was meant
; 6) line 32, "free ?gripper" should be put inside round brackets, you need in fact the bracket after the not

(define (domain gripper-strips)
   (:requirements :strips :typing)
   (:types ball gripper room)
   (:predicates
        (at-robby ?r - room)
        (at ?b - cube ?r - room)
        (free g - gripper)
        (carry ?o - ball ?g - gripper)
		(turned-off ?g - gripper))
	
   (:action move
       :parameter  (?from ?to - room)
       :precondition (and at-robby ?from)
       :effect (and  (at-robby ?to)
             (not (at-robby ?from))))	

	
   (:action pick
       :parameters (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (at ?obj ?room) (at-robby ?room) (free ?gri))
       :effect (and (carry ?obj ?gripper)
		    (not (at ?obj ?room)) 
		    (not free ?gripper)))


   (:action drop
       :parameters  (?obj - ball ?room - room ?gripper - gripper)
       :precondition  (and (carry ?obj ?gripper) (at-robby ?room))
       :effect (and (at ?obj ?room)
		    (free ?gripper)
		    (not (carry ?obj ?gripper)))))
