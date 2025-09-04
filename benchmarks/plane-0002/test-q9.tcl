model Basic -ndm 2 -ndf 2

material ElasticIsotropic 1 10000.0 0.25 0 
section PlaneStress 1 1 1.0 

node 1 0.0 -5.0 
node 2 8.333333333333332 -5.0 
node 3 16.666666666666668 -5.000000000000001 
node 4 25.0 -5.0 
node 5 33.33333333333333 -5.0 
node 6 41.666666666666664 -5.0 
node 7 50.0 -5.0 
node 8 0.0 0.0 
node 9 16.666666666666668 0.0 
node 10 33.33333333333333 0.0 
node 11 50.0 0.0 
node 12 0.0 5.0 
node 13 8.333333333333332 5.0 
node 14 16.666666666666668 5.000000000000001 
node 15 25.0 5.0 
node 16 33.33333333333333 5.0 
node 17 41.666666666666664 5.0 
node 18 50.0 5.0 
node 19 8.333333333333332 0.0 
node 20 25.0 0.0 
node 21 41.666666666666664 0.0

fix  1 1 0 
fix  8 1 1 
fix 12 1 0 

element quad 1 {1 3 14 12 2  9 13  8 19} -section 1
element quad 2 {3 5 16 14 4 10 15  9 20} -section 1
element quad 3 {5 7 18 16 6 11 17 10 21} -section 1

pattern Plain 1 Linear {
  load 7 0 -2.000000000000001 
  load 11 0 -16.0 
  load 18 0 -2.0000000000000018 
  load 1 0 2.000000000000001 
  load 8 0 16.0 
  load 12 0 2.0000000000000018 
}

integrator LoadControl 1.0 
analysis Static 
analyze 1 

