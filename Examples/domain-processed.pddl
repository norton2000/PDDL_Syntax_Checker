(define (domain gripper-strips)
	(:requirements :strips :negative-preconditions)
	(:predicates
		(room ?r)
		(ball ?b)
		(gripper ?g)
		(at-robby ?r)
		(at ?b ?r)
		(free ?g)
		(carry ?o ?g)
	)

	(:action move
		:parameters (?ehi ?from ?to)
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)))
	)

	(:action pick
		:parameters (?obj ?room ?gripper)
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper) (at-robby ?room))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)))
	)

)