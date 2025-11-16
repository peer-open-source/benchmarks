pragma openseespy
model  -ndm 3 -ndf 3
material J2 1 -E 100.0 -nu 0.3 -Fy 15.0 -Hiso 0.0 -Hkin 0.0 -Hsat 50.0 -Fs 25.0
node 1 0.0 0.0 0.0 
node 2 10.0 0.0 0.0 
node 3 10.0 10.0 0.0 
node 4 0.0 10.0 0.0 
node 5 0.0 0.0 10.0 
node 6 10.0 0.0 10.0 
node 7 10.0 10.0 10.0 
node 8 0.0 10.0 10.0 
element bbarBrick 1 1 2 3 4 5 6 7 8 1 

timeSeries Path 101 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 101 101 
sp 1 1 1.0 -pattern 101
timeSeries Path 102 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 102 102 
sp 1 2 1.0 -pattern 102
timeSeries Path 103 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 103 103 
sp 1 3 1.0 -pattern 103
timeSeries Path 104 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 104 104 
sp 2 1 1.0 -pattern 104
timeSeries Path 105 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 105 105 
sp 2 2 1.0 -pattern 105
timeSeries Path 110 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 110 110 
sp 4 1 1.0 -pattern 110
timeSeries Path 111 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 111 111 
sp 4 2 1.0 -pattern 111
timeSeries Path 112 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 112 112 
sp 4 3 1.0 -pattern 112
timeSeries Path 107 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 107 107 
sp 3 1 1.0 -pattern 107
timeSeries Path 108 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 108 108 
sp 3 2 1.0 -pattern 108

timeSeries Path 106 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 106 106 
sp 2 3 1.0 -pattern 106
timeSeries Path 109 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 109 109 
sp 3 3 1.0 -pattern 109
timeSeries Path 113 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 113 113 
sp 5 1 1.0 -pattern 113
timeSeries Path 114 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 114 114 
sp 5 2 1.0 -pattern 114
timeSeries Path 115 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 7.0 0.0 0.0 0.0 7.0 0.0}
pattern Plain 115 115 
sp 5 3 1.0 -pattern 115
timeSeries Path 116 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 116 116 
sp 6 1 1.0 -pattern 116
timeSeries Path 117 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 117 117 
sp 6 2 1.0 -pattern 117
timeSeries Path 118 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 7.0 6.0 -6.0 6.0 7.0 6.0}
pattern Plain 118 118 
sp 6 3 1.0 -pattern 118
timeSeries Path 119 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 119 119 
sp 7 1 1.0 -pattern 119
timeSeries Path 120 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 120 120 
sp 7 2 1.0 -pattern 120
timeSeries Path 121 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 7.0 6.0 -6.0 6.0 7.0 6.0}
pattern Plain 121 121 
sp 7 3 1.0 -pattern 121
timeSeries Path 122 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 6.0 -6.0 6.0 0.0 6.0 -6.0 6.0 0.0 6.0}
pattern Plain 122 122 
sp 8 1 1.0 -pattern 122
timeSeries Path 123 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0}
pattern Plain 123 123 
sp 8 2 1.0 -pattern 123
timeSeries Path 124 -time {0 1 3 5 6 7 9 11 12 13} -values {0.0 0.0 0.0 0.0 7.0 0.0 0.0 0.0 7.0 0.0}
pattern Plain 124 124 
sp 8 3 1.0 -pattern 124

system FullGeneral 
numberer Plain 
constraints Transformation 
test Energy 1e-20 10 0
integrator LoadControl 0.013 
algorithm Newton 
analysis Static 
verify value [analyze 1000] 0

eleResponse 1 stress 1 
eleResponse 1 strains 1 
