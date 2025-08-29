
model basic -ndm 3 -ndf 6 

section ElasticMembranePlateSection 1 10000.0 0.0 1.0 

node 1 0.0 0.0 0.0 
node 2 1.0 0.0 0.0 
node 3 2.0 0.0 0.0 
node 4 3.0 0.0 0.0 
node 5 4.0 0.0 0.0 
node 6 5.0 0.0 0.0 
node 7 6.0 0.0 0.0 
node 8 7.0 0.0 0.0 
node 9 8.0 0.0 0.0 
node 10 9.0 0.0 0.0 
node 11 10.0 0.0 0.0 
node 12 11.0 0.0 0.0 
node 13 12.0 0.0 0.0 
node 14 13.0 0.0 0.0 
node 15 14.0 0.0 0.0 
node 16 15.0 0.0 0.0 
node 17 16.0 0.0 0.0 
node 18 17.0 0.0 0.0 
node 19 18.0 0.0 0.0 
node 20 19.0 0.0 0.0 
node 21 20.0 0.0 0.0 
node 22 0.0 1.0 0.0 
node 23 1.0 1.0 0.0 
node 24 2.0 1.0 0.0 
node 25 3.0 1.0 0.0 
node 26 4.0 1.0 0.0 
node 27 5.0 1.0 0.0 
node 28 6.0 1.0 0.0 
node 29 7.0 1.0 0.0 
node 30 8.0 1.0 0.0 
node 31 9.0 1.0 0.0 
node 32 10.0 1.0 0.0 
node 33 11.0 1.0 0.0 
node 34 12.0 1.0 0.0 
node 35 13.0 1.0 0.0 
node 36 14.0 1.0 0.0 
node 37 15.0 1.0 0.0 
node 38 16.0 1.0 0.0 
node 39 17.0 1.0 0.0 
node 40 18.0 1.0 0.0 
node 41 19.0 1.0 0.0 
node 42 20.0 1.0 0.0 
element ASDShellT3  1 1 2 23 1 -corotational 
element ASDShellT3  2 1 23 22 1 -corotational 
element ASDShellT3  3 2 3 23 1 -corotational 
element ASDShellT3  4 3 24 23 1 -corotational 
element ASDShellT3  5 3 4 25 1 -corotational 
element ASDShellT3  6 3 25 24 1 -corotational 
element ASDShellT3  7 4 5 25 1 -corotational 
element ASDShellT3  8 5 26 25 1 -corotational 
element ASDShellT3  9 5 6 27 1 -corotational 
element ASDShellT3 10 5 27 26 1 -corotational 
element ASDShellT3 11 6 7 27 1 -corotational 
element ASDShellT3 12 7 28 27 1 -corotational 
element ASDShellT3 13 7 8 29 1 -corotational 
element ASDShellT3 14 7 29 28 1 -corotational 
element ASDShellT3 15 8 9 29 1 -corotational 
element ASDShellT3 16 9 30 29 1 -corotational 
element ASDShellT3 17 9 10 31 1 -corotational 
element ASDShellT3 18 9 31 30 1 -corotational 
element ASDShellT3 19 10 11 31 1 -corotational 
element ASDShellT3 20 11 32 31 1 -corotational 
element ASDShellT3 21 11 12 33 1 -corotational 
element ASDShellT3 22 11 33 32 1 -corotational 
element ASDShellT3 23 12 13 33 1 -corotational 
element ASDShellT3 24 13 34 33 1 -corotational 
element ASDShellT3 25 13 14 35 1 -corotational 
element ASDShellT3 26 13 35 34 1 -corotational 
element ASDShellT3 27 14 15 35 1 -corotational 
element ASDShellT3 28 15 36 35 1 -corotational 
element ASDShellT3 29 15 16 37 1 -corotational 
element ASDShellT3 30 15 37 36 1 -corotational 
element ASDShellT3 31 16 17 37 1 -corotational 
element ASDShellT3 32 17 38 37 1 -corotational 
element ASDShellT3 33 17 18 39 1 -corotational 
element ASDShellT3 34 17 39 38 1 -corotational 
element ASDShellT3 35 18 19 39 1 -corotational 
element ASDShellT3 36 19 40 39 1 -corotational 
element ASDShellT3 37 19 20 41 1 -corotational 
element ASDShellT3 38 19 41 40 1 -corotational 
element ASDShellT3 39 20 21 41 1 -corotational 
element ASDShellT3 40 21 42 41 1 -corotational 
fix 1 1 1 1 1 1 1 
fix 22 1 1 1 1 1 1 

timeSeries Linear 1
pattern Plain 1 1 {
  load 21 0 0 0 0 -261.79938779914943 0
  load 42 0 0 0 0 -261.79938779914943 0
}

constraints Transformation 
numberer RCM 
system UmfPack 
test NormDispIncr 1e-05 100 0
algorithm Newton 
integrator LoadControl 0.025 
analysis Static 
analyze 40 



verify value [nodeDisp [expr (20+1)*(1+1)] 3]   0       1e-10
verify value [nodeDisp [expr (20+1)*(1+1)] 5] -12.56637 1e-6
