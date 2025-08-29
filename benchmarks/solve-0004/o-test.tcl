foreach algorithm {KrylovNewton SecantNewton ModifiedNewton} {
  wipe
  model basic -ndm 1 -ndf 1 
  node 0 0 
  node 1 0 
  node 2 0 
  fix 0 1 

  uniaxialMaterial Steel01 1 10 10 0.1 
  uniaxialMaterial Steel01 2 4 2 0.5 
  uniaxialMaterial Steel01 3 7 7 0 

  element zeroLength 1 0 1 -mat 1 -dir 1 
  element zeroLength 2 1 2 -mat 2 -dir 1 
  element zeroLength 3 0 2 -mat 3 -dir 1 
  uniaxialMaterial Elastic 0 0 
  uniaxialMaterial Penalty 4 0 -1 -noStress 
  element zeroLength 4 0 1 -mat 4 -dir 1 
  uniaxialMaterial Penalty 5 0 -0.5 -noStress 
  element zeroLength 5 1 2 -mat 5 -dir 1 
  uniaxialMaterial Penalty 6 0 0.5 -noStress 
  element zeroLength 6 0 1 -mat 6 -dir 1 
  element zeroLength 7 0 2 -mat 6 -dir 1 
  timeSeries Constant 1 
  pattern Plain 1 1 
  nodalLoad 1 6 -pattern 1 
  nodalLoad 2 12 -pattern 1 
  test RelativeNormUnbalance 0.0001 150
  algorithm KrylovNewton 
  analysis Static 
  analyze 1 

  verify value [nodeDisp 1 ] 2.0
  verify value [nodeDisp 2 ] 5.0
}
