(define (domain restaurant)
	(:requirements :strips :negative-preconditions :typing)
	(:types 
		robot customer - object
		entry table position - boxes
	)

	(:predicates
		(at ?x - object ?y - boxes)
		(adjacent ?x - boxes ?y - boxes)
		(nearkitchen ?x - boxes)
		(reserved ?x - table ?y - customer)
		(occupied ?x - boxes)
		(hold ?x - robot ?z - customer)
		(serving ?x - robot)
		(focuson ?x - robot ?y - customer)
		(thinking ?x - customer)
		(takeordination ?x - robot ?y - customer)
		(orderreadyfor ?x - robot ?y - customer)
		(havefinished ?x - customer)
		(bye ?x - customer)
		(notarrived ?x - customer)
	)

	(:action move
		:parameters (?who - robot ?from - boxes ?to - boxes)
		:precondition (and (adjacent ?from ?to) (not (occupied ?to)) (at ?who ?from) (not (at ?who ?to)))
		:effect (and (at ?who ?to) (not (at ?who ?from)) (occupied ?to) (not (occupied ?from)))
	)

	(:action takecustomer
		:parameters (?who - robot ?other - robot ?customer - customer ?where - entry)
		:precondition (and (at ?who ?where) (not (at ?other ?where)) (not (serving ?who)) (at ?customer ?where) (not (havefinished ?customer)))
		:effect (and (not (at ?customer ?where)) (hold ?who ?customer) (serving ?who))
	)

	(:action takecustomerend
		:parameters (?who - robot ?customer - customer ?where - boxes ?table - table)
		:precondition (and (at ?who ?where) (havefinished ?customer) (at ?customer ?table) (adjacent ?where ?table) (focuson ?who ?customer))
		:effect (and (not (at ?customer ?where)) (hold ?who ?customer) (serving ?who) (not (occupied ?table)) (not (reserved ?table ?customer)))
	)

	(:action leaveattable
		:parameters (?who - robot ?customer - customer ?from - boxes ?table - table)
		:precondition (and (at ?who ?from) (adjacent ?from ?table) (hold ?who ?customer) (or (not (occupied ?table)) (reserved ?table ?customer)))
		:effect (and (not (hold ?who ?customer)) (at ?customer ?table) (thinking ?customer) (occupied ?table) (focuson ?who ?customer))
	)

	(:action takeorder
		:parameters (?robot - robot ?position - boxes ?table - table ?customer - customer)
		:precondition (and (at ?robot ?position) (at ?customer ?table) (adjacent ?position ?table) (thinking ?customer) (focuson ?robot ?customer))
		:effect (and (not (thinking ?customer)) (takeordination ?robot ?customer))
	)

	(:action prepareordination
		:parameters (?robot - robot ?pos - boxes ?customer - customer)
		:precondition (and (at ?robot ?pos) (nearkitchen ?pos) (takeordination ?robot ?customer))
		:effect (and (not (takeordination ?robot ?customer)) (orderreadyfor ?robot ?customer))
	)

	(:action giveordination
		:parameters (?robot - robot ?pos - boxes ?table - table ?customer - customer)
		:precondition (and (at ?robot ?pos) (adjacent ?pos ?table) (orderreadyfor ?robot ?customer))
		:effect (and (not (orderreadyfor ?robot ?customer)) (havefinished ?customer))
	)

	(:action saygoodbye
		:parameters (?robot - robot ?pos - entry ?customer - customer)
		:precondition (and (at ?robot ?pos) (hold ?robot ?customer) (havefinished ?customer))
		:effect (and (not (hold ?robot ?customer)) (bye ?customer) (not (serving ?robot)) (not (focuson ?robot ?customer)))
	)

	(:action newcustomer
		:parameters (?c1 - customer ?c2 - customer ?p - entry)
		:precondition (and (bye ?c2) (notarrived ?c1))
		:effect (and (at ?c1 ?p) (not (notarrived ?c1)))
	)

)