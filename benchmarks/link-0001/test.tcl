set k 10.0
set L 10.0
set P  5.0

model basic -ndm 2 -ndf 3
node 0 0 0 
node 1 0 0
node 2 0 $L
fix 0 1 1 1 
fix 1 1 0 1 
fix 2 1 0 1 

uniaxialMaterial Elastic 1 $k
element zeroLength 1 0 1 -mat 1 -dir 1 -orient 0 1 0 
element twoNodeLink 2 0 2 -mat 1 -dir 1 

pattern Plain 1 Constant 
nodalLoad 1 0 $P 0 -pattern 1 
nodalLoad 2 0 $P 0 -pattern 1 
analysis Static 
analyze 1 

verify value [nodeDisp 1 2] [expr $P/$k]
verify value [nodeDisp 2 2] [expr $P/$k]
