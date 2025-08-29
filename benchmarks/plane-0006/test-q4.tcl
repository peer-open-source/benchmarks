
model  -ndm 2 -ndf 2
material ElasticIsotropic 1 4000.0 0.25 0 
section PlaneStress 1 1 1.0 

node  1   0.0 0.0 
node  2  20.0 0.0 
node  3  40.0 0.0 
node  4  60.0 0.0 
node  5  80.0 0.0 
node  6 100.0 0.0 
node  7 120.0 0.0 
node  8 140.0 0.0 
node  9 160.0 0.0 
node 10 180.0 0.0 
node 11 200.0 0.0 
node 12 220.0 0.0 
node 13 240.0 0.0 
node 14   0.0 6.0 
node 15  20.0 6.0 
node 16  40.0 6.0
node 17  60.0 6.0 
node 18  80.0 6.0 
node 19 100.0 6.0 
node 20 120.0 6.0 
node 21 140.0 6.0 
node 22 160.0 6.0 
node 23 180.0 6.0 
node 24 200.0 6.0 
node 25 220.0 6.0
node 26 240.0 6.0 
node 27 0.0 12.0 
node 28 20.0 12.0 
node 29 39.99999999999999 12.0 
node 30 60.0 12.0 
node 31 80.0 12.000000000000002 
node 32 100.0 12.0 
node 33 120.0 12.0 
node 34 140.0 12.0 
node 35 160.0 12.0 
node 36 180.0 12.0 
node 37 200.0 12.0 
node 38 220.0 12.0 
node 39 240.0 12.0 
node 40 0.0 18.0 
node 41 20.0 18.0 
node 42 39.999999999999986 18.0 
node 43 60.0 18.0 
node 44 80.0 18.0 
node 45 100.0 18.0 
node 46 120.0 18.0 
node 47 140.0 18.0 
node 48 160.0 18.0 
node 49 180.0 18.0 
node 50 200.0 18.0 
node 51 220.0 18.0 
node 52 240.0 18.0 
node 53 0.0 24.0 
node 54 20.0 24.0 
node 55 39.99999999999999 24.0 
node 56 60.0 24.0 
node 57 80.0 24.0 
node 58 100.0 24.0 
node 59 120.0 24.0 
node 60 140.0 24.000000000000004 
node 61 160.0 24.0 
node 62 180.0 24.0 
node 63 200.0 24.0 
node 64 220.0 24.0 
node 65 240.0 24.0 
element quad  1 { 1  2 15 14} -section 1
element quad  2 { 2  3 16 15} -section 1
element quad  3 { 3  4 17 16} -section 1
element quad  4 { 4  5 18 17} -section 1
element quad  5 { 5  6 19 18} -section 1
element quad  6 { 6  7 20 19} -section 1
element quad  7 { 7  8 21 20} -section 1
element quad  8 { 8  9 22 21} -section 1
element quad  9 { 9 10 23 22} -section 1
element quad 10 {10 11 24 23} -section 1
element quad 11 {11 12 25 24} -section 1
element quad 12 {12 13 26 25} -section 1
element quad 13 {14 15 28 27} -section 1
element quad 14 {15 16 29 28} -section 1
element quad 15 {16 17 30 29} -section 1
element quad 16 {17 18 31 30} -section 1
element quad 17 {18 19 32 31} -section 1
element quad 18 {19 20 33 32} -section 1
element quad 19 {20 21 34 33} -section 1
element quad 20 {21 22 35 34} -section 1
element quad 21 {22 23 36 35} -section 1
element quad 22 {23 24 37 36} -section 1
element quad 23 {24 25 38 37} -section 1
element quad 24 {25 26 39 38} -section 1
element quad 25 {27 28 41 40} -section 1
element quad 26 {28 29 42 41} -section 1
element quad 27 {29 30 43 42} -section 1
element quad 28 {30 31 44 43} -section 1
element quad 29 {31 32 45 44} -section 1
element quad 30 {32 33 46 45} -section 1
element quad 31 {33 34 47 46} -section 1
element quad 32 {34 35 48 47} -section 1
element quad 33 {35 36 49 48} -section 1
element quad 34 {36 37 50 49} -section 1
element quad 35 {37 38 51 50} -section 1
element quad 36 {38 39 52 51} -section 1
element quad 37 {40 41 54 53} -section 1
element quad 38 {41 42 55 54} -section 1
element quad 39 {42 43 56 55} -section 1
element quad 40 {43 44 57 56} -section 1
element quad 41 {44 45 58 57} -section 1
element quad 42 {45 46 59 58} -section 1
element quad 43 {46 47 60 59} -section 1
element quad 44 {47 48 61 60} -section 1
element quad 45 {48 49 62 61} -section 1
element quad 46 {49 50 63 62} -section 1
element quad 47 {50 51 64 63} -section 1
element quad 48 {51 52 65 64} -section 1
fix 1 1 1 
fix 14 1 1 
fix 27 1 1 
fix 40 1 1 
fix 53 1 1 
fix 13 1 1 
fix 26 1 1 
fix 39 1 1 
fix 52 1 1 
fix 65 1 1 

pattern Plain 1 Linear {
  load  2 0 -0.833333333333333  
  load  3 0 -0.833333333333333  
  load  3 0 -0.8333333333333336  
  load  4 0 -0.8333333333333336  
  load  4 0 -0.8333333333333333  
  load  5 0 -0.8333333333333333  
  load  5 0 -0.8333333333333333  
  load  6 0 -0.8333333333333333  
  load  6 0 -0.8333333333333333  
  load  7 0 -0.8333333333333333  
  load  7 0 -0.8333333333333333  
  load  8 0 -0.8333333333333333  
  load  8 0 -0.8333333333333333  
  load  9 0 -0.8333333333333333  
  load  9 0 -0.8333333333333333  
  load 10 0 -0.8333333333333333  
  load 10 0 -0.8333333333333333  
  load 11 0 -0.8333333333333333  
  load 11 0 -0.8333333333333333  
  load 12 0 -0.8333333333333333  
}

integrator LoadControl 1.0 
analysis Static 
verify value [analyze 1] 0

