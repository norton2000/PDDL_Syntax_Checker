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
