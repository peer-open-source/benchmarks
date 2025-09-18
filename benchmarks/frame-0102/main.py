#
# Chopra example 12.6
#
# Sept 8, 2025
#
import os
from xara.benchmarks import Prism
import xara.units.iks as units
from xsection.library import Rectangle
import numpy as np


def analyze(model):

    series = np.loadtxt("elCentro.txt")
    model.timeSeries("Path", 1, values=series, dt=0.02)

    model.pattern("UniformExcitation", 1, 3, accel=1)

    model.integrator("Newmark", beta=0.25, gamma=0.5)
    model.analysis("Transient")
    model.test("Residual", 1e-9, 20, 2)

    u = []
    for i in range(len(series)):
        if model.analyze(1, 0.02) != 0:
            raise RuntimeError("Analysis failed at step %d" % i)
        u.append(model.nodeDisp(2))

    return np.array(u)



if __name__ == "__main__":
    shape = Rectangle(d=14, b=10, mesh_scale=1/100)

    E  = 29e3*units.ksi
    G  = 11.2e3*units.ksi # * 4/5

    A  = shape.cnn()[0,0]
    GA = A*G
    EI = E*shape.cmm()[1,1]

    L = shape.d*4
    for shear in [0]:
        prism = Prism(shape=shape,
                      length=L,
                      boundary=((1,1,1,  1,1,1),
                                (0,0,0,  0,0,0)),
                      material={"name": "ElasticIsotropic", "E": E, "G": G},
                      element=os.environ.get("Element", "ForceFrame"),
                      section=os.environ.get("Section", "ShearFiber"),
                      shear=shear,
                      mass=10000,
                      divisions=1
                )
        model = prism.create_model()

        u = analyze(model)
        print(max(u[:,2]))
