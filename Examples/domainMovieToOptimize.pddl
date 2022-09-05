; In this file there is another domain: movie-to-optimize, based on the pddl movie domain, contains some modifications.
; There are 2 new actions "go-to-ticket-office" and "take-the-ticket".
; It is intended to show that, using the file "problemMovie.pddl" as the problem, since the two added actions must necessarily be performed in sequence, the optimizer will recognize it and combine them into a single action.
; Not only that, the optimizer will also recognize rewind-movie-2 as a non-executable action (counter-at-two-hours, the precondition of the action cannot become true in any way) and then delete it.
; Note how if from the problemMovie.pddl you delete in the goal for example "have-chips" then the action "get-chips" will also be found to be useless to execute in the current problem and thus will be removed by the optimizer.
; The command to perform this optimization is: 
; python .\syntaxChecker.py -d Examples\domainMovieToOptimize.pddl -p Examples\problemMovie.pddl -o


(define (domain movie-to-optimize)
  (:requirements :typing)
  (:types food)
  (:predicates (movie-rewound)
               (counter-at-two-hours)
	       (counter-at-other-than-two-hours)
               (counter-at-zero)
			   (stay-at-ticket-office)
			   (have-ticket)
               (have-chips)
               (have-dip)
               (have-pop)
               (have-cheese)
               (have-crackers)
               (chips ?x - food)
               (dip ?x - food)
               (pop ?x - food)
               (cheese ?x - food)
               (crackers ?x - food))
  
  (:action rewind-movie-2
           :parameters ()
	   :precondition (counter-at-two-hours)
           :effect (movie-rewound))
  
  (:action rewind-movie
           :parameters ()
	   :precondition (counter-at-other-than-two-hours)
           :effect (and (movie-rewound)
                        ;; Let's assume that the movie is 2 hours long
                        (not (counter-at-zero))))

  (:action reset-counter
           :parameters () 
           :precondition (and)
           :effect (counter-at-zero))


  ;;; Get the food and snacks for the movie
  (:action get-chips
           :parameters (?x - food)
           :precondition (chips ?x)
           :effect (have-chips))
  
  (:action get-dip
           :parameters (?x - food)
           :precondition (dip ?x)
           :effect (have-dip))

  (:action get-pop
           :parameters (?x - food)
           :precondition (pop ?x)
           :effect (have-pop))
  
  (:action get-cheese
           :parameters (?x - food)
           :precondition (cheese ?x)
           :effect (have-cheese))
  
  (:action get-crackers
           :parameters (?x - food)
           :precondition (crackers ?x)
           :effect (have-crackers))
   
  (:action go-to-ticket-office
		   :parameters ()
		   :precondition (and)
		   :effect (stay-at-ticket-office))
		   
  (:action take-the-ticket
		   :parameters ()
		   :precondition (stay-at-ticket-office)
		   :effect (and (not (stay-at-ticket-office))
						(have-ticket))))