pragma openseespy
model  -ndm 3 -ndf 6
node 1 0 0 0 
node 2 120.0 0 0 
fix 1 1 1 1 1 1 1 
material ElasticIsotropic 1 29000.0 0.3 
section ElasticFrame 1 -E 29000.0 -G 11153.846153846154 -A 14.129434810887911 -Ay 14.129434810887911 -Az 14.129434810887911 -Iy 484.66344952846396 -Iz 51.4238877625387 -J 1.4502399084989293
geomTransf Linear 1 0 0 1 
element ForceFrame 1 1 2 -section 1 -transform 1 -shear 0
wipeAnalysis  
test Residual 1e-08 2 
setTime 0.0 
pattern Plain 1 Linear 
nodalLoad 2 0.0 0.0 0.0 1000.0 0.0 0.0 -pattern 1 
algorithm Newton 
analysis Static 
analyze 1 
wipeAnalysis  
loadConst  -time 0.0
nodeDisp 2 4 
