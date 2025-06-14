---
title: Shell undergoing finite rotations
render: circle.glb
thumbnail: img/examples/ShellCircle.png
tags: ["Shell"]
description: Geometrically nonlinear analysis of a cantilever rolling up under the action of a point moment, performed with shell finite elements.
downloads:
  Tcl:    ["test-q4.tcl", "test-p3.tcl"]
---


Here we investigate the roll-up problem previously considered for [frames](../framecircle), now with corotational shells.


The loading is applied in 40 increments.

In the Python version, we'll create a [`veux.Artist`](https://veux.io/library/artist/index.html) before starting the analysis
in order to draw snapshots of the deformed shape throughout the deformation.
```python
# Render the reference configuration
artist = veux.create_artist(model, vertical=3)
artist.draw_surfaces()
artist.draw_outlines()
```

Now we proceed to [`analyze`](https://xara.so/user/manual/analysis/analyze.html):
```python
u = []
load = []
for i in range(nsteps):
    if ops.analyze(1) != 0:
        break
    ctime += dt
    if ctime > dt_record:
        ctime = 0.0
        artist.draw_outlines(state=ops.nodeDisp)

    load[i+1] = ops.getTime()
    u[i+1]   =  ops.nodeDisp(tip, 3)
```


After running the Python variant of the analysis, the following plot is generated:

![Nodal displacements and rotations](img/plot.png)

# References

- https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.6/books/bmk/default.htm?startat=ch02s01ach122.html

