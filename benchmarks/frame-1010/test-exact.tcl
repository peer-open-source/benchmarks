
model  -ndm 3 -ndf 6
node  1   0.0               0.0                0.0 
node  2  11.999850000312499 0.0599997500003125 0.0 
node  3  23.999700000624998 0.1199995000006250 0.0 
node  4  35.999550000937500 0.1799992500009375 0.0 
node  5  47.999400001249995 0.2399990000012500 0.0 
node  6  59.999250001562500 0.2999987500015625 0.0 
node  7  71.999100001875000 0.3599985000018750 0.0 
node  8  83.998950002187500 0.4199982500021875 0.0 
node  9  95.998800002499990 0.4799980000025000 0.0 
node 10 107.998650002812500 0.5399977500028125 0.0 
node 11 119.998500003125000 0.5999975000031250 0.0 
node 12 131.998350003437500 0.6599972500034375 0.0 
node 13 143.998200003750000 0.7199970000037500 0.0 
node 14 155.998050004062500 0.7799967500040624 0.0 
node 15 167.997900004375000 0.8399965000043750 0.0 
node 16 179.997750004687500 0.8999962500046874 0.0 
node 17 191.997600004999980 0.9599960000050000 0.0 
node 18 203.997450005312500 1.0199957500053125 0.0 
node 19 215.997300005625000 1.079995500005625 0.0 
node 20 227.997150005937500 1.1399952500059374 0.0 
node 21 239.997000006250000 1.19999500000625 0.0 

fix  1 1 1 1 1 1 1 
fix 21 0 1 1 0 1 1 

section ElasticFrame 1 -E 71240 -G 27190 -A 10.0 -J 2.16 -Iy 0.0833 -Iz 0.0833 -Ay 10.0 -Az 10.0 
geomTransf Linear 1 0.0 0.0 1.0 
element ExactFrame  1  1  2 -section 1 -transform 1 -shear 1
element ExactFrame  2  2  3 -section 1 -transform 1 -shear 1
element ExactFrame  3  3  4 -section 1 -transform 1 -shear 1
element ExactFrame  4  4  5 -section 1 -transform 1 -shear 1
element ExactFrame  5  5  6 -section 1 -transform 1 -shear 1
element ExactFrame  6  6  7 -section 1 -transform 1 -shear 1
element ExactFrame  7  7  8 -section 1 -transform 1 -shear 1
element ExactFrame  8  8  9 -section 1 -transform 1 -shear 1
element ExactFrame  9  9 10 -section 1 -transform 1 -shear 1
element ExactFrame 10 10 11 -section 1 -transform 1 -shear 1
element ExactFrame 11 11 12 -section 1 -transform 1 -shear 1
element ExactFrame 12 12 13 -section 1 -transform 1 -shear 1
element ExactFrame 13 13 14 -section 1 -transform 1 -shear 1
element ExactFrame 14 14 15 -section 1 -transform 1 -shear 1
element ExactFrame 15 15 16 -section 1 -transform 1 -shear 1
element ExactFrame 16 16 17 -section 1 -transform 1 -shear 1
element ExactFrame 17 17 18 -section 1 -transform 1 -shear 1
element ExactFrame 18 18 19 -section 1 -transform 1 -shear 1
element ExactFrame 19 19 20 -section 1 -transform 1 -shear 1
element ExactFrame 20 20 21 -section 1 -transform 1 -shear 1

pattern Plain 1 Linear {
  load 21 0 0 0 49.451815179204495 0.24726113640892672 0.0 ;
}

test NormDispIncr 1e-09 52 0
integrator MinUnbalDispNorm 1 5 1.5384615384615384e-05 1 
system Umfpack 
analysis Static 

nodeDisp 21 4 
getTime  
getLoadFactor 1 
analyze 400
nodeDisp 21 4 
getTime
getLoadFactor 1 

