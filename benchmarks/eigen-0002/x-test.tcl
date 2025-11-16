foreach solver {symmGenLapack fullGenLapack} {
  model basic -ndm 1 -ndf 1
  node 0 0 
  fix  0 1 
  node 1 0 
  mass 1 1.0 
  node 2 0 
  mass 2 1.0 
  node 3 0 
  mass 3 1.0 
  node 4 0 
  mass 4 1.0 
  uniaxialMaterial Elastic 1 610 
  element zeroLength 1 0 1 -mat 1 -dir 1 
  element zeroLength 2 1 2 -mat 1 -dir 1 
  element zeroLength 3 0 3 -mat 1 -dir 1 
  element zeroLength 4 3 4 -mat 1 -dir 1 

  set values [eigen $solver 3]

  foreach value $values reference {232.99926686256413 232.99926686256413 1597.0007331374356} {
    verify value $value $reference 1e-10
  }

# verify value [nodeEigenvector 1 1 1 ]  0.0
# verify value [nodeEigenvector 2 1 1 ]  0.0
# verify value [nodeEigenvector 3 1 1 ]  0.5257311121191337 1e-10
# verify value [nodeEigenvector 4 1 1 ]  0.8506508083520399 1e-10
# 
# verify value [nodeEigenvector 1 2 1 ]  0.5257311121191337 1e-10
# verify value [nodeEigenvector 2 2 1 ]  0.8506508083520399 1e-10
# verify value [nodeEigenvector 3 2 1 ]  0.0
# verify value [nodeEigenvector 4 2 1 ]  0.0
# 
# verify value [nodeEigenvector 1 3 1 ]  0.0
# verify value [nodeEigenvector 2 3 1 ]  0.0
# verify value [nodeEigenvector 3 3 1 ]  0.8506508083520399 1e-10
# verify value [nodeEigenvector 4 3 1 ] -0.5257311121191335 1e-10
  wipe
}
