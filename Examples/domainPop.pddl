(define (domain restaurant)

 (:requirements
  :strips                 
  :negative-preconditions
  :typing
  ;:fluents
  ;:disjunctive-preconditions
  )
 (:types 
 robot customer - object
 entry table position - boxes
 )
 (:predicates (at ?x - object ?y - boxes)  (adjacent ?x - boxes ?Y - boxes) (nearKitchen ?x - boxes)
 ;table x booked by y
 (reserved ?x - table ?y - customer) 
 ;box occupied by a robot or table occupied by customers
 (occupied ?x - boxes) 
 ; the robot takes customers 
 (hold ?x - robot ?z - customer)
 ;The robot is already serving other customers.
 (serving ?x - robot)
 ;robot must now serve only those customers
 (focusOn ?x - robot ?y - customer)
 ;customers have to think about ordering
 (thinking ?x - customer)
 ;robot x takes order for customer Y
 (takeordination ?x - robot ?y - customer)
 ;kitchen has finished preparing the order of robot x for customers y
 (orderReadyfor ?x - robot ?y - customer)
 ;customers have finished and want to leave
 (haveFinished ?x - customer)
 ;the customer left satisfied.
 (bye ?x - customer)
 ;a customer with a reservation who has not yet arrived
 (notArrived ?x - customer)
)
 ;function that calculates the working time of robots
 ;(:functions
 ;(workingTime ?x - robot)
 ;)

 (:action move
  :parameters(?who - robot ?from - boxes ?to - boxes)
  :precondition(and
  (adjacent ?from ?to)
  (not(occupied ?to))
  (at ?who ?from)
  (not(at ?who ?to))
  )
  :effect(and
  (at ?who ?to)
  (not(at ?who ?from))
  (occupied ?to)
  (not(occupied ?from))
  ;(increase (workingTime ?who) 1)
  )
 )
 ;robot welcomes customers
 (:action takeCustomer
    :parameters (?who - robot ?other - robot ?customer - customer  ?where - entry )
    :precondition (and
    (at ?who ?where)
    ;who e other non sono lo stesso robot
    (not (at ?other ?where))
    (not(serving ?who)) (at ?customer ?where)  (not(haveFinished ?customer)) 
    ;the robot can take the customer if the customer is not impatient, otherwise the goal fails. 
	;calculate the customer's patience as the sum of the working time of both waiters
    ;(<= (+(workingTime ?other) (workingTime ?who)) 150))
    )
    :effect ( and
    (not(at ?customer ?where))
    (hold ?who ?customer)
    (serving ?who)
    ;(increase (workingTime ?who) 1)
    )
  )
;robot picks up customers to accompany them to the exit
(:action takeCustomerEnd
    :parameters(?who - robot ?customer - customer  ?where - boxes ?table - table)
    :precondition(and
    (at ?who ?where)
    (haveFinished ?customer)
    (at ?customer ?table)
    (adjacent ?where ?table)
    (focusOn ?who ?customer))
    :effect(and
    (not(at ?customer	?where))
    (hold ?who ?customer)
    (serving ?who)
    ;(increase (workingTime ?who) 1)
    (not(occupied ?table))
    (not(reserved ?table ?customer))
    )
)

;robot leaves customers at their table
(:action leaveAtTable
    :parameters(?who - robot ?customer - customer ?from - boxes ?table - table)
    :precondition(and
    (at ?who ?from)
    (adjacent ?from ?table)
    (hold ?who ?customer)
    (or (not(occupied ?table))
    (reserved ?table ?customer))
    )
    :effect(and
    (not(hold ?who ?customer))
    (at ?customer ?table)
    (thinking ?customer)
    (occupied ?table)
    (focusOn ?who ?customer)
    ;(increase (workingTime ?who) 1)
    ))

;robot takes order
(:action takeOrder
    :parameters(?robot - robot ?position - boxes ?table - table ?customer - customer)
    :precondition(and
    (at ?robot ?position)
    (at ?customer ?table)
    (adjacent  ?position ?table)
    (thinking ?customer)
    (focusOn ?robot ?customer)
    )
    ;the customer is no longer thinking. he will have spent time thinking.
    :effect(and
    (not(thinking ?customer))
    ;(increase (workingTime ?robot) 5)
    (takeordination ?robot ?customer)
    ;(takeordination  ?customer)
    )
)

;robot brings order to the kitchen and the kitchen prepares it, finally giving it to the robot 
(:action prepareOrdination
    :parameters(?robot - robot ?pos - boxes ?customer - customer)
    :precondition(and
    (at ?robot ?pos)
    (nearKitchen ?pos)
    (takeordination  ?robot ?customer)
    )
    :effect(and
    (not(takeordination  ?robot ?customer))
    ;la cucina riceve l'ordinazione e la prepara in un certo tempo 
    ;(increase (workingTime ?robot) 5)
    (orderReadyfor ?robot ?customer)
    )
)

;robot delivers the order to the customers and they eat
(:action giveOrdination
    :parameters(?robot - robot ?pos - boxes ?table - table ?customer - customer)
    :precondition(and
    (at ?robot ?pos)
    (adjacent ?pos ?table)
    (orderReadyfor ?robot ?customer)
    )
    :effect(and
    ;(increase (workingTime ?robot) 5)
    (not(orderReadyfor ?robot ?customer))
    (haveFinished ?customer)
    )
)

;the robot greets departing customers at the entrance
(:action sayGoodbye
    :parameters(?robot - robot ?pos - entry ?customer - customer)
    :precondition(and
    (at ?robot ?pos)
    (hold ?robot ?customer)
    (haveFinished ?customer)
    )
    :effect(and
    (not(hold ?robot ?customer))
    (bye ?customer )
    (not(serving ?robot))
    ;(increase (workingTime ?robot) 1)
    ;(decrease(customerPatience ?customer) (workingTime ?robot))
    (not (focusOn ?robot ?customer))
    )
)
;the customer arrives with a table reservation after the previous one has left
(:action newCustomer
    :parameters (?c1 - customer  ?c2 - customer ?p - entry)
    :precondition (and 
        (bye ?c2)
        (notArrived ?c1) 
    )
    :effect (and 
        (at ?c1 ?p)
        (not(notArrived ?c1))
    )
)
)