(define (domain gripper-strips)
	(:requirements :strips :typing)
	(:types 
		ball
		gripper
		room
	)

	(:predicates
		(at-robby ?r - room)
		(at ?b - ball ?r - room)
		(free ?g - gripper)
		(carry ?o - ball ?g - gripper)
		(object-in-position-to-grab ?g - gripper ?o - ball ?r - room)
	)

	(:action move
		:parameters (?from - room ?to - room)
		:precondition (and (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)))
	)

	(:action drop
		:parameters (?obj - ball ?room - room ?gripper - gripper)
		:precondition (and (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))
	)

	(:action prepare_grab-grab
		:parameters (?room ?gripper ?obj)
		:precondition (and (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)) (object-in-position-to-grab ?gripper ?obj ?room))
	)

)