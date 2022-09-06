(define (domain movie-to-optimize)
	(:requirements :typing)
	(:types 
		food
	)

	(:predicates
		(movie-rewound )
		(counter-at-two-hours )
		(counter-at-other-than-two-hours )
		(counter-at-zero )
		(stay-at-ticket-office )
		(have-ticket )
		(have-chips )
		(have-dip )
		(have-pop )
		(have-cheese )
		(have-crackers )
		(chips ?x - food)
		(dip ?x - food)
		(pop ?x - food)
		(cheese ?x - food)
		(crackers ?x - food)
	)

	(:action rewind-movie
		:parameters ()
		:precondition (counter-at-other-than-two-hours )
		:effect (and (movie-rewound ) (not (counter-at-zero )))
	)

	(:action reset-counter
		:parameters ()
		:precondition (and )
		:effect (counter-at-zero )
	)

	(:action get-chips
		:parameters (?x - food)
		:precondition (chips ?x)
		:effect (have-chips )
	)

	(:action get-dip
		:parameters (?x - food)
		:precondition (dip ?x)
		:effect (have-dip )
	)

	(:action get-pop
		:parameters (?x - food)
		:precondition (pop ?x)
		:effect (have-pop )
	)

	(:action get-cheese
		:parameters (?x - food)
		:precondition (cheese ?x)
		:effect (have-cheese )
	)

	(:action get-crackers
		:parameters (?x - food)
		:precondition (crackers ?x)
		:effect (have-crackers )
	)

	(:action go-to-ticket-office-take-the-ticket
		:parameters ()
		:precondition (and )
		:effect (and (not (stay-at-ticket-office )) (have-ticket ))
	)

)