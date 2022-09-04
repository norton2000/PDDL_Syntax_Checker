; Pddl problem file containing some typical errors to show how the program behaves in front of them.
; The errors in particular are:
; 1) line 8, there is a object "square1" of type "square" but this type does not exist in the domain
; 2) line 12, The predicate "free" wants an object of type "gripper", instead it was given an object of type "ball"

(define (problem strips-gripper-x-1)
   (:domain gripper-strips)
   (:objects rooma roomb - room ball4 ball3 ball2 ball1 - ball left right - gripper square1 - square)
   (:init (at-robby rooma)
          (free left)
          (free right)
		  (free ball2)
          (at ball4 rooma)
          (at ball3 rooma)
          (at ball2 rooma)
          (at ball1 rooma))
   (:goal (and (at ball4 roomb)
               (at ball3 roomb)
               (at ball2 roomb)
               (at ball1 roomb))))