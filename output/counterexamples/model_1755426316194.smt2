; countermodel
(define-fun a () Int
  1)
(define-fun b () Int
  1)
(define-fun f ((x!0 Int)) Int
  (ite (= x!0 1) 1
  (ite (= x!0 2) 2
    x!0)))
